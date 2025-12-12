"""
CUDA Engine - GPU acceleration for computational tasks
"""
import numpy as np
from typing import Any, Dict, List, Optional
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class CUDAEngine:
    """
    CUDA/GPU acceleration engine
    Falls back to CPU if CUDA is not available
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.cuda_available = False
        self.device_id = get_config('system', 'cuda.device_id', 0)
        self.enabled = get_config('system', 'cuda.enabled', False)
        
        if self.enabled:
            self._initialize_cuda()
        else:
            self.logger.info("CUDA disabled in configuration, using CPU")
    
    def _initialize_cuda(self):
        """Initialize CUDA if available"""
        try:
            import cupy as cp
            self.cp = cp
            self.cuda_available = True
            
            # Get device info
            device = cp.cuda.Device(self.device_id)
            self.logger.info(f"CUDA initialized on device {self.device_id}: {device.compute_capability}")
            
        except ImportError:
            self.logger.warning("CuPy not installed, falling back to CPU")
            self.cuda_available = False
        except Exception as e:
            self.logger.warning(f"CUDA initialization failed: {e}, falling back to CPU")
            self.cuda_available = False
    
    def to_device(self, array: np.ndarray):
        """
        Transfer numpy array to GPU
        
        Args:
            array: NumPy array
            
        Returns:
            GPU array if available, otherwise CPU array
        """
        if self.cuda_available:
            return self.cp.asarray(array)
        return array
    
    def to_host(self, array):
        """
        Transfer array from GPU to CPU
        
        Args:
            array: GPU or CPU array
            
        Returns:
            NumPy array
        """
        if self.cuda_available and isinstance(array, self.cp.ndarray):
            return self.cp.asnumpy(array)
        return np.asarray(array)
    
    def matrix_multiply(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Perform matrix multiplication (GPU accelerated if available)
        
        Args:
            a: First matrix
            b: Second matrix
            
        Returns:
            Result matrix
        """
        if self.cuda_available:
            a_gpu = self.to_device(a)
            b_gpu = self.to_device(b)
            result_gpu = self.cp.matmul(a_gpu, b_gpu)
            return self.to_host(result_gpu)
        else:
            return np.matmul(a, b)
    
    def compute_correlation(self, data: np.ndarray) -> np.ndarray:
        """
        Compute correlation matrix (GPU accelerated if available)
        
        Args:
            data: Input data matrix
            
        Returns:
            Correlation matrix
        """
        if self.cuda_available:
            data_gpu = self.to_device(data)
            corr_gpu = self.cp.corrcoef(data_gpu.T)
            return self.to_host(corr_gpu)
        else:
            return np.corrcoef(data.T)
    
    def fft(self, signal: np.ndarray) -> np.ndarray:
        """
        Compute Fast Fourier Transform (GPU accelerated if available)
        
        Args:
            signal: Input signal
            
        Returns:
            FFT result
        """
        if self.cuda_available:
            signal_gpu = self.to_device(signal)
            fft_gpu = self.cp.fft.fft(signal_gpu)
            return self.to_host(fft_gpu)
        else:
            return np.fft.fft(signal)
    
    def convolve(self, signal: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Compute convolution (GPU accelerated if available)
        
        Args:
            signal: Input signal
            kernel: Convolution kernel
            
        Returns:
            Convolved signal
        """
        if self.cuda_available:
            signal_gpu = self.to_device(signal)
            kernel_gpu = self.to_device(kernel)
            result_gpu = self.cp.convolve(signal_gpu, kernel_gpu)
            return self.to_host(result_gpu)
        else:
            return np.convolve(signal, kernel)
    
    def parallel_compute(self, func, data_list: List[np.ndarray]) -> List[np.ndarray]:
        """
        Compute function on multiple arrays in parallel
        
        Args:
            func: Function to apply
            data_list: List of input arrays
            
        Returns:
            List of results
        """
        results = []
        
        if self.cuda_available:
            # Transfer all to GPU
            gpu_data = [self.to_device(data) for data in data_list]
            
            # Compute (CuPy operations are already async)
            gpu_results = [func(data) for data in gpu_data]
            
            # Transfer back
            results = [self.to_host(result) for result in gpu_results]
        else:
            # CPU computation
            results = [func(data) for data in data_list]
        
        return results
    
    def is_available(self) -> bool:
        """Check if CUDA is available"""
        return self.cuda_available
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get CUDA device information"""
        if not self.cuda_available:
            return {
                'available': False,
                'device': 'CPU'
            }
        
        try:
            device = self.cp.cuda.Device(self.device_id)
            free_mem, total_mem = device.mem_info
            
            return {
                'available': True,
                'device': 'GPU',
                'device_id': self.device_id,
                'compute_capability': device.compute_capability,
                'total_memory_mb': total_mem / (1024 * 1024),
                'free_memory_mb': free_mem / (1024 * 1024),
                'used_memory_mb': (total_mem - free_mem) / (1024 * 1024)
            }
        except Exception as e:
            self.logger.error(f"Error getting device info: {e}")
            return {'available': False, 'error': str(e)}
    
    def clear_cache(self):
        """Clear GPU memory cache"""
        if self.cuda_available:
            try:
                self.cp.get_default_memory_pool().free_all_blocks()
                self.logger.info("Cleared GPU memory cache")
            except Exception as e:
                self.logger.error(f"Error clearing GPU cache: {e}")


# Global CUDA engine instance
_cuda_engine = None


def get_cuda_engine() -> CUDAEngine:
    """Get or create global CUDA engine instance"""
    global _cuda_engine
    if _cuda_engine is None:
        _cuda_engine = CUDAEngine()
    return _cuda_engine
