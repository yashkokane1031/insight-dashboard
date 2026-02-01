"""
Heavy Load Data Generator for InSight

This script simulates 1000+ IoT sensors pumping high-frequency data 
into TimescaleDB to stress-test the real-time analytics dashboard.

Features:
- Configurable number of sensors (default: 1000)
- Configurable write frequency (default: 100 writes/sec)
- Realistic data patterns (sinusoidal + noise + occasional spikes)
- Direct database insertion for maximum throughput
- Performance metrics logging

Usage:
    python data_generator.py --sensors 1000 --interval 0.01 --duration 60

Arguments:
    --sensors: Number of simulated sensors (default: 1000)
    --interval: Seconds between batches (default: 0.1)
    --duration: Total runtime in seconds (default: 60, 0 = infinite)
    --batch-size: Number of inserts per batch (default: 100)
"""

import argparse
import time
import random
import math
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import psycopg2
from psycopg2.extras import execute_values
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# Database configuration (matches docker-compose.yml)
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "insightdb",
    "user": "user",
    "password": "password"
}


class SensorSimulator:
    """Generates realistic sensor data with patterns."""
    
    def __init__(self, sensor_id: int, base_temp: float = 65.0):
        self.sensor_id = sensor_id
        self.base_temp = base_temp + random.uniform(-10, 10)  # Slight variation per sensor
        self.noise_level = random.uniform(1, 5)
        self.phase = random.uniform(0, 2 * math.pi)  # Random phase offset
        self.spike_probability = 0.001  # 0.1% chance of spike
    
    def generate_value(self, time_offset: float) -> float:
        """Generate a realistic temperature value."""
        # Sinusoidal base pattern (simulates daily temperature cycle)
        cycle = math.sin(time_offset / 300 + self.phase) * 10
        
        # Random noise
        noise = random.gauss(0, self.noise_level)
        
        # Occasional spikes (anomalies)
        spike = 0
        if random.random() < self.spike_probability:
            spike = random.choice([20, -15, 25, -10])  # Sudden jump
        
        value = self.base_temp + cycle + noise + spike
        return round(max(30, min(100, value)), 2)  # Clamp between 30-100


class LoadGenerator:
    """Manages high-frequency data generation and insertion."""
    
    def __init__(self, num_sensors: int, batch_size: int):
        self.num_sensors = num_sensors
        self.batch_size = batch_size
        self.sensors = [SensorSimulator(i) for i in range(num_sensors)]
        self.connection = None
        self.total_inserts = 0
        self.start_time = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            logger.info(f"Connected to database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from database")
    
    def generate_batch(self, time_offset: float) -> list:
        """Generate a batch of data points."""
        # Select random sensors for this batch
        selected_sensors = random.sample(self.sensors, min(self.batch_size, len(self.sensors)))
        
        batch = []
        for sensor in selected_sensors:
            value = sensor.generate_value(time_offset)
            batch.append((
                f"sensor_{sensor.sensor_id}",  # name
                value,                          # value
                datetime.now(timezone.utc)      # timestamp
            ))
        
        return batch
    
    def insert_batch(self, batch: list):
        """Insert a batch of data points into the database."""
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        try:
            with self.connection.cursor() as cursor:
                execute_values(
                    cursor,
                    "INSERT INTO data_points (name, value, timestamp) VALUES %s",
                    batch
                )
            self.connection.commit()
            self.total_inserts += len(batch)
        except psycopg2.Error as e:
            logger.error(f"Insert failed: {e}")
            self.connection.rollback()
    
    def run(self, interval: float, duration: float):
        """
        Run the load generator.
        
        Args:
            interval: Seconds between batches
            duration: Total runtime in seconds (0 = infinite)
        """
        self.start_time = time.time()
        iteration = 0
        last_log_time = self.start_time
        inserts_since_last_log = 0
        
        logger.info(f"Starting load generator:")
        logger.info(f"  - Sensors: {self.num_sensors}")
        logger.info(f"  - Batch size: {self.batch_size}")
        logger.info(f"  - Interval: {interval}s")
        logger.info(f"  - Duration: {'infinite' if duration == 0 else f'{duration}s'}")
        logger.info("-" * 50)
        
        try:
            while True:
                iteration_start = time.time()
                time_offset = iteration_start - self.start_time
                
                # Check duration
                if duration > 0 and time_offset >= duration:
                    break
                
                # Generate and insert batch
                batch = self.generate_batch(time_offset)
                self.insert_batch(batch)
                inserts_since_last_log += len(batch)
                
                # Log stats every 5 seconds
                current_time = time.time()
                if current_time - last_log_time >= 5:
                    elapsed = current_time - last_log_time
                    rate = inserts_since_last_log / elapsed
                    total_elapsed = current_time - self.start_time
                    
                    logger.info(
                        f"Writes/sec: {rate:.1f} | "
                        f"Total: {self.total_inserts:,} | "
                        f"Elapsed: {total_elapsed:.0f}s"
                    )
                    
                    last_log_time = current_time
                    inserts_since_last_log = 0
                
                # Sleep to maintain interval
                elapsed = time.time() - iteration_start
                sleep_time = max(0, interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                iteration += 1
                
        except KeyboardInterrupt:
            logger.info("\nStopped by user")
        
        # Final stats
        total_time = time.time() - self.start_time
        avg_rate = self.total_inserts / total_time if total_time > 0 else 0
        
        logger.info("=" * 50)
        logger.info("FINAL STATS")
        logger.info(f"  Total inserts: {self.total_inserts:,}")
        logger.info(f"  Total time: {total_time:.1f}s")
        logger.info(f"  Average rate: {avg_rate:.1f} writes/sec")


def main():
    parser = argparse.ArgumentParser(description="InSight Heavy Load Data Generator")
    parser.add_argument("--sensors", type=int, default=1000, help="Number of simulated sensors")
    parser.add_argument("--interval", type=float, default=0.1, help="Seconds between batches")
    parser.add_argument("--duration", type=float, default=60, help="Total runtime in seconds (0 = infinite)")
    parser.add_argument("--batch-size", type=int, default=100, help="Number of inserts per batch")
    
    args = parser.parse_args()
    
    generator = LoadGenerator(args.sensors, args.batch_size)
    
    try:
        generator.connect()
        generator.run(args.interval, args.duration)
    finally:
        generator.disconnect()


if __name__ == "__main__":
    main()
