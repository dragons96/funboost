
import random
import time

from funboost import boost, FunctionResultStatusPersistanceConfig,BoosterParams
from funboost.core.current_task import funboost_current_task
from funboost.core.task_id_logger import TaskIdLogger
import nb_log
from funboost.funboost_config_deafult import FunboostCommonConfig
from nb_log import LogManager

LOG_FILENAME_QUEUE_FCT = 'queue_fct.log'
logger = LogManager('namexx',logger_cls=TaskIdLogger).get_logger_and_add_handlers(
                                 log_filename='queue_fct.log',
                                 error_log_filename=nb_log.generate_error_file_name(LOG_FILENAME_QUEUE_FCT),
                                 formatter_template=FunboostCommonConfig.NB_LOG_FORMATER_INDEX_FOR_CONSUMER_AND_PUBLISHER, )

@boost(BoosterParams(queue_name='queue_test_fct', qps=2,concurrent_num=5,log_filename=LOG_FILENAME_QUEUE_FCT))
def f(a, b):
    fct = funboost_current_task() # 线程/协程隔离级别的上下文

    fct.logger.warning('如果不想亲自创建logger对象，可以使用fct.logger来记录日志，fct.logger是当前队列的消费者logger对象')
    logger.info(fct.function_result_status.task_id) # 获取消息的任务id
    logger.debug(fct.function_result_status.run_times) # 获取消息是第几次重试运行
    logger.info(fct.full_msg) # 获取消息的完全体。出了a和b的值意外，还有发布时间 task_id等。
    logger.debug(fct.function_result_status.publish_time) # 获取消息的发布时间
    logger.debug(fct.function_result_status.get_status_dict()) # 获取任务的信息，可以转成字典看。

    time.sleep(2)
    if random.random() > 0.99:
        raise Exception(f'{a} {b} 模拟出错啦')
    logger.debug(f'哈哈 a: {a}')
    logger.debug(f'哈哈 b: {b}')
    logger.info(a+b)


    return a + b


if __name__ == '__main__':
    # f(5, 6)  # 可以直接调用

    for i in range(0, 200):
        f.push(i, b=i * 2)

    f.consume()