# import numpy as np
# import itertools
# from multiprocessing import Pool #  Process pool
# from multiprocessing import sharedctypes

# size = 100
# block_size = 4

# X = np.random.random((size, size))
# result = np.ctypeslib.as_ctypes(np.zeros((size, size)))
# shared_array = sharedctypes.RawArray(result._type_, result)


# def fill_per_window(args):
#     window_x, window_y = args
#     tmp = np.ctypeslib.as_array(shared_array)
#     # print(len(tmp))
#     for idx_x in range(window_x, window_x + block_size):
#         for idx_y in range(window_y, window_y + block_size):
#             tmp[idx_x, idx_y] = X[idx_x, idx_y]


# window_idxs = [(i, j) for i, j in
#                itertools.product(range(0, size, block_size),
#                                  range(0, size, block_size))]
# # print(np.array(window_idxs).shape)

# p = Pool()
# res = p.map(fill_per_window, window_idxs)
# result = np.ctypeslib.as_array(shared_array)

# print(np.array_equal(X, result))


# import time
# from multiprocessing import Pool
# def run(fn):
#   time.sleep(1)
#   return fn*fn

# if __name__ == "__main__":
#   testFL = [1,2,3,4,5,6]  
#   e1 = time.time()
#   print('concurrent:') #创建多个进程，并行执行
#   pool = Pool(5)  #创建拥有5个进程数量的进程池
#   #testFL:要处理的数据列表，run：处理testFL列表中数据的函数
#   rl =pool.map(run, testFL) 
#   pool.close()#关闭进程池，不再接受新的进程
#   pool.join()#主进程阻塞等待子进程的退出
#   e2 = time.time()
#   print("并行执行时间：", int(e2-e1))
#   print(rl)


import numpy as np
import time
from multiprocessing import Pool, RawArray

def worker_func(i):
    X_np[i] = np.arange(4)

if __name__ == '__main__':
    X_shape = (2, 4)
    data = np.random.randn(*X_shape)
    X = RawArray('d', X_shape[0] * X_shape[1])
    X_np = np.frombuffer(X).reshape(X_shape)
    np.copyto(X_np, data)
    pool = Pool(processes = 4)
    result = pool.map(worker_func, range(X_shape[0]))
    pool.close()
    pool.join()
    tmp = np.ma.array(X_np[0])
    tmp = np.ma.masked_less_equal(tmp, 2)
    print('Results (numpy):\n', X_np)