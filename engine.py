"""
LagForge - Core Packet Delay Engine
Implements real-time packet interception, Gaussian jitter, packet drop probability,
delay injection, and real-time bandwidth / throughput measurement using WinDivert.
"""

import sys
import time
import queue
import random
import logging
import threading
from typing import Optional

from PySide6.QtCore import QObject, Signal

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(threadName)s: %(message)s")
logger = logging.getLogger("LagForge.Engine")

try:
    import pydivert
    HAS_PYDIVERT = True
except ImportError:
    HAS_PYDIVERT = False
    logger.warning("pydivert module not found. Engine will run in simulation mode.")


class PacketDelayEngine(QObject):
    """
    Main controller for the network latency engine.
    Supports fixed latency, Gaussian jitter, packet drop simulation, and real-time throughput metrics.
    """

    started = Signal()
    stopped = Signal()
    error_occurred = Signal(str)
    telemetry_updated = Signal(int, int, float, float, float, float, float, float)
    # (total_delayed, total_dropped, pps, inbound_ms, outbound_ms, kbps_in, kbps_out, sparkline_point)

    def __init__(self, filter_rule: str = "!loopback", parent: Optional[QObject] = None):
        super().__init__(parent)
        self.filter_rule = filter_rule
        self._target_ping_ms: float = 325.0
        self._jitter_ms: float = 0.0
        self._packet_loss_pct: float = 0.0
        self._is_active: bool = False

        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._capture_thread: Optional[threading.Thread] = None
        self._sender_thread: Optional[threading.Thread] = None
        self._telemetry_thread: Optional[threading.Thread] = None

        self._stop_event = threading.Event()
        self._divert_handle: Optional[object] = None
        self._seq_counter = 0

        # Stats
        self._total_delayed_packets: int = 0
        self._total_dropped_packets: int = 0
        self._recent_delayed_packets: int = 0
        self._recent_dropped_packets: int = 0
        self._recent_bytes_in: int = 0
        self._recent_bytes_out: int = 0
        self._lock = threading.Lock()

    @property
    def target_ping_ms(self) -> float:
        return self._target_ping_ms

    @target_ping_ms.setter
    def target_ping_ms(self, val: float):
        with self._lock:
            self._target_ping_ms = max(0.0, float(val))

    @property
    def jitter_ms(self) -> float:
        return self._jitter_ms

    @jitter_ms.setter
    def jitter_ms(self, val: float):
        with self._lock:
            self._jitter_ms = max(0.0, min(100.0, float(val)))

    @property
    def packet_loss_pct(self) -> float:
        return self._packet_loss_pct

    @packet_loss_pct.setter
    def packet_loss_pct(self, val: float):
        with self._lock:
            self._packet_loss_pct = max(0.0, min(25.0, float(val)))

    @property
    def is_active(self) -> bool:
        return self._is_active

    def calculate_effective_latency_ms(self) -> float:
        with self._lock:
            base_ping = self._target_ping_ms
            jitter = self._jitter_ms

        if jitter <= 0.001:
            return base_ping

        sigma = jitter / 2.0
        noise = random.gauss(0, sigma)
        bounded_noise = max(-jitter, min(jitter, noise))
        return max(0.0, base_ping + bounded_noise)

    def should_drop_packet(self) -> bool:
        with self._lock:
            loss_pct = self._packet_loss_pct

        if loss_pct <= 0.001:
            return False
        return (random.random() * 100.0) < loss_pct

    def start(self, target_ping_ms: Optional[float] = None, jitter_ms: Optional[float] = None, packet_loss_pct: Optional[float] = None):
        if self._is_active:
            return

        if target_ping_ms is not None:
            self.target_ping_ms = target_ping_ms
        if jitter_ms is not None:
            self.jitter_ms = jitter_ms
        if packet_loss_pct is not None:
            self.packet_loss_pct = packet_loss_pct

        self._stop_event.clear()
        self._is_active = True

        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

        self._capture_thread = threading.Thread(
            target=self._capture_worker, name="LagForge-CaptureWorker", daemon=True
        )
        self._sender_thread = threading.Thread(
            target=self._sender_worker, name="LagForge-SenderWorker", daemon=True
        )
        self._telemetry_thread = threading.Thread(
            target=self._telemetry_worker, name="LagForge-TelemetryWorker", daemon=True
        )

        self._capture_thread.start()
        self._sender_thread.start()
        self._telemetry_thread.start()

        self.started.emit()
        logger.info(f"Engine started. Ping: {self._target_ping_ms}ms ±{self._jitter_ms}ms (Loss: {self._packet_loss_pct}%)")

    def stop(self):
        if not self._is_active:
            return

        logger.info("Stopping engine...")
        self._is_active = False
        self._stop_event.set()

        if self._divert_handle is not None:
            try:
                self._divert_handle.close()
            except Exception as e:
                logger.debug(f"Error closing WinDivert handle: {e}")
            self._divert_handle = None

        self._flush_queue()

        for t in (self._capture_thread, self._sender_thread, self._telemetry_thread):
            if t and t.is_alive():
                t.join(timeout=0.3)

        self.stopped.emit()
        logger.info("Engine stopped safely.")

    def _flush_queue(self):
        count = 0
        while not self._queue.empty():
            try:
                _, _, packet = self._queue.get_nowait()
                if self._divert_handle is not None and hasattr(self._divert_handle, "send"):
                    try:
                        self._divert_handle.send(packet)
                    except Exception:
                        pass
                count += 1
            except queue.Empty:
                break
        if count > 0:
            logger.info(f"Flushed {count} lingering packets on shutdown.")

    def _capture_worker(self):
        if not HAS_PYDIVERT:
            self._simulate_capture_worker()
            return

        try:
            self._divert_handle = pydivert.WinDivert(filter=self.filter_rule)
            self._divert_handle.open()
        except PermissionError:
            err = "Administrator privileges required to open WinDivert driver."
            logger.error(err)
            self.error_occurred.emit(err)
            self._stop_event.set()
            self._is_active = False
            return
        except Exception as e:
            err = f"Failed to initialize WinDivert handle: {e}"
            logger.error(err)
            self.error_occurred.emit(err)
            self._stop_event.set()
            self._is_active = False
            return

        logger.info("WinDivert capture handle opened successfully.")

        try:
            while not self._stop_event.is_set():
                try:
                    packet = self._divert_handle.recv()
                    if packet is None:
                        continue

                    # Record bandwidth stats
                    pkt_len = len(packet.raw) if hasattr(packet, "raw") and packet.raw else 128
                    is_inbound = getattr(packet, "is_inbound", True)

                    with self._lock:
                        if is_inbound:
                            self._recent_bytes_in += pkt_len
                        else:
                            self._recent_bytes_out += pkt_len

                    # Check for simulated packet loss
                    if self.should_drop_packet():
                        with self._lock:
                            self._total_dropped_packets += 1
                            self._recent_dropped_packets += 1
                        continue

                    # Calculate effective ping with jitter
                    effective_ping = self.calculate_effective_latency_ms()
                    half_delay_sec = (effective_ping / 2.0) / 1000.0

                    if half_delay_sec <= 0.0001:
                        try:
                            self._divert_handle.send(packet)
                        except Exception:
                            pass
                    else:
                        release_time = time.perf_counter() + half_delay_sec
                        self._seq_counter = (self._seq_counter + 1) & 0x7FFFFFFF
                        self._queue.put((release_time, self._seq_counter, packet))

                    with self._lock:
                        self._total_delayed_packets += 1
                        self._recent_delayed_packets += 1

                except Exception as ex:
                    if self._stop_event.is_set():
                        break
                    logger.debug(f"Capture loop recv exception: {ex}")
                    time.sleep(0.001)

        finally:
            if self._divert_handle is not None:
                try:
                    self._divert_handle.close()
                except Exception:
                    pass
                self._divert_handle = None

    def _sender_worker(self):
        while not self._stop_event.is_set():
            try:
                if self._queue.empty():
                    time.sleep(0.0008)
                    continue

                item = self._queue.get(timeout=0.005)
                release_time, seq, packet = item

                now = time.perf_counter()
                delay_remaining = release_time - now

                if delay_remaining > 0.002:
                    time.sleep(delay_remaining - 0.001)
                    while time.perf_counter() < release_time:
                        pass
                elif delay_remaining > 0.0:
                    while time.perf_counter() < release_time:
                        pass

                if not self._stop_event.is_set() and self._divert_handle is not None:
                    try:
                        self._divert_handle.send(packet)
                    except Exception as e:
                        logger.debug(f"Error sending packet: {e}")

            except queue.Empty:
                continue
            except Exception as ex:
                if not self._stop_event.is_set():
                    logger.debug(f"Sender worker exception: {ex}")

    def _simulate_capture_worker(self):
        while not self._stop_event.is_set():
            sim_burst = random.randint(5, 25)
            sim_drop = 1 if self.should_drop_packet() else 0
            bytes_in = sim_burst * random.randint(128, 1400)
            bytes_out = sim_burst * random.randint(64, 800)

            with self._lock:
                self._total_delayed_packets += sim_burst
                self._recent_delayed_packets += sim_burst
                self._total_dropped_packets += sim_drop
                self._recent_dropped_packets += sim_drop
                self._recent_bytes_in += bytes_in
                self._recent_bytes_out += bytes_out
            time.sleep(0.05)

    def _telemetry_worker(self):
        last_time = time.perf_counter()
        while not self._stop_event.is_set():
            time.sleep(0.05)
            now = time.perf_counter()
            dt = max(0.001, now - last_time)
            last_time = now

            with self._lock:
                total_cnt = self._total_delayed_packets
                dropped_cnt = self._total_dropped_packets
                recent_cnt = self._recent_delayed_packets
                bytes_in = self._recent_bytes_in
                bytes_out = self._recent_bytes_out
                self._recent_delayed_packets = 0
                self._recent_bytes_in = 0
                self._recent_bytes_out = 0
                ping_ms = self._target_ping_ms

            pps = recent_cnt / dt
            kbps_in = (bytes_in / 1024.0) / dt
            kbps_out = (bytes_out / 1024.0) / dt
            half_ms = ping_ms / 2.0
            sparkline_val = pps if self._is_active else 0.0

            self.telemetry_updated.emit(
                total_cnt,
                dropped_cnt,
                pps,
                half_ms,
                half_ms,
                kbps_in,
                kbps_out,
                sparkline_val
            )
