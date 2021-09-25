# -*- encoding: utf-8 -*-

import traceback
from typing import List, Tuple, Optional

import arrow
import regex as re
from loguru import logger

OP = {'>=', '<=', '='}
SMALL_MONTH = ['04', '06', '09', '11']


def str2int(s: str) -> int:
    """将字符串数字转为整数

    :param s: 字符串数字
    
    :return: 对应的整形数，如果不是数字返回0
    """
    try:
        res = int(s)
    except Exception:
        res = 0
    return res


def word2number(s: str) -> int:
    """方法number_translator的辅助方法，可将[零-九]正确翻译为[0-9]
    
    :param s: 大写数字
    
    :return: 对应的整形数，如果不是数字返回-1
    """
    return {
        "零": 0,
        "0": 0,
        "一": 1,
        "1": 1,
        "二": 2,
        "两": 2,
        "2": 2,
        "三": 3,
        "3": 3,
        "四": 4,
        "4": 4,
        "五": 5,
        "5": 5,
        "六": 6,
        "6": 6,
        "七": 7,
        "7": 7,
        "八": 8,
        "8": 8,
        "九": 9,
        "9": 9,
    }.get(s, -1)


def number_translator(target: str) -> str:
    """
    该方法可以将字符串中所有的用汉字表示的数字转化为用阿拉伯数字表示的数字
    如"这里有一千两百个人，六百零五个来自中国"可以转化为
    "这里有1200个人，605个来自中国"
    此外添加支持了部分不规则表达方法
    如两万零六百五可转化为20650
    两百一十四和两百十四都可以转化为214
    一六零加一五八可以转化为160+158
    该方法目前支持的正确转化范围是: 0 ~ 10^16 - 1
    该功能模块具有良好的复用性
    
    :param target: 待转化的字符串
    :return: 转化完毕后的字符串
    """
    # logger.debug(f"before number_translator: {target}")
    
    # 省略叫法: 六亿五
    pattern = re.compile(r"[一二两三四五六七八九123456789]亿[一二两三四五六七八九123456789](?!(万|千|百|十))")
    match = pattern.finditer(target)
    for m in match:
        group = m.group()
        s = group.split("亿")
        s = list(filter(None, s))
        num = 0
        if len(s) == 2:
            num += word2number(s[0]) * 10 ** 8 + word2number(s[1]) * 10 ** 7
        target = pattern.sub(str(num), target, 1)
    
    # 省略叫法: 六万五
    pattern = re.compile(r"[一二两三四五六七八九123456789]万[一二两三四五六七八九123456789](?!(千|百|十))")
    match = pattern.finditer(target)
    for m in match:
        group = m.group()
        s = group.split("万")
        s = list(filter(None, s))
        num = 0
        if len(s) == 2:
            num += word2number(s[0]) * 10000 + word2number(s[1]) * 1000
        target = pattern.sub(str(num), target, 1)
        
    # 省略叫法: 六千五
    pattern = re.compile(r"[一二两三四五六七八九123456789]千[一二两三四五六七八九123456789](?!(百|十))")
    match = pattern.finditer(target)
    for m in match:
        group = m.group()
        s = group.split("千")
        s = list(filter(None, s))
        num = 0
        if len(s) == 2:
            num += word2number(s[0]) * 1000 + word2number(s[1]) * 100
        target = pattern.sub(str(num), target, 1)

    # 省略叫法: 六百五
    pattern = re.compile(r"[一二两三四五六七八九123456789]百[一二两三四五六七八九123456789](?!十)")
    match = pattern.finditer(target)
    for m in match:
        group = m.group()
        s = group.split("百")
        s = list(filter(None, s))
        num = 0
        if len(s) == 2:
            num += word2number(s[0]) * 100 + word2number(s[1]) * 10
        target = pattern.sub(str(num), target, 1)


    # 将单位前的文字先转为数字
    pattern = re.compile(r"[零一二两三四五六七八九]")
    match = pattern.finditer(target)
    for m in match:
        target = pattern.sub(str(word2number(m.group())), target, 1)

    # 星期天表达式替换为星期7
    pattern = re.compile("(?<=(周|星期))[末天日]")
    match = pattern.finditer(target)
    for m in match:
        target = pattern.sub("7", target, 1)

    # 转化单位`十`
    pattern = re.compile("(?<!(周|星期))0?[0-9]?十[0-9]?")
    match = pattern.finditer(target)
    for m in match:
        group = m.group()
        s = group.split("十")
        num = 0
        ten = str2int(s[0])
        if ten == 0:
            ten = 1
        unit = str2int(s[1])
        num = ten * 10 + unit
        target = pattern.sub(str(num), target, 1)
        
    # 转化单位`百`
    pattern = re.compile("0?[1-9]百[0-9]?[0-9]?")
    match = pattern.finditer(target)
    for m in match:
        group = m.group()
        s = group.split("百")
        s = list(filter(None, s))
        num = 0
        if len(s) == 1:
            hundred = int(s[0])
            num += hundred * 100
        elif len(s) == 2:
            hundred = int(s[0])
            num += hundred * 100
            num += int(s[1])
        target = pattern.sub(str(num), target, 1)
        
    # 转化单位`千`
    pattern = re.compile("0?[1-9]千[0-9]?[0-9]?[0-9]?")
    match = pattern.finditer(target)
    for m in match:
        group = m.group()
        s = group.split("千")
        s = list(filter(None, s))
        num = 0
        if len(s) == 1:
            thousand = int(s[0])
            num += thousand * 1000
        elif len(s) == 2:
            thousand = int(s[0])
            num += thousand * 1000
            num += int(s[1])
        target = pattern.sub(str(num), target, 1)
        
    # 转化单位`万`
    pattern = re.compile("[0-9]+万[0-9]?[0-9]?[0-9]?[0-9]?")
    match = pattern.finditer(target)
    for m in match:
        group = m.group()
        s = group.split("万")
        s = list(filter(None, s))
        num = 0
        if len(s) == 1:
            tenthousand = int(s[0])
            num += tenthousand * 10000
        elif len(s) == 2:
            tenthousand = int(s[0])
            num += tenthousand * 10000
            num += int(s[1])
        target = pattern.sub(str(num), target, 1)
        
    # 转化单位`亿`
    pattern = re.compile("[0-9]+亿[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?")
    match = pattern.finditer(target)
    for m in match:
        group = m.group()
        s = group.split("亿")
        s = list(filter(None, s))
        num = 0
        if len(s) == 1:
            yi = int(s[0])
            num += yi * 10 ** 8
        elif len(s) == 2:
            yi = int(s[0])
            num += yi * 10 ** 8
            num += int(s[1])
        target = pattern.sub(str(num), target, 1)
    # logger.debug(f"after number_translator: {target}")
    return target


def year_trans(text: str) -> List:
    """年份的转换, 返回一个时间段, 粒度为`天` 
    
    `最近3年`, 从当天往前推算3年
    `前3年`, 计算本年之前三个完整年份
    
    `n年前`, n = {1,2,3}, 返回往前推算n年的整个年份; n = {4}, 返回该年度上一年的最后一天
    `n年后`, n = {1,2,3}, 返回大于往后推算n年的今; n = {4}, 返回大于该年度的1号

    Args:
        text (str): 输入文本

    Returns:
        List: 年份的开始和结束年月日
        
    Examples:
        >>> year_trans('去年下半年')
        ['2020-07-01', '2020-12-31']
        
        >>> year_trans('最近半年')
        ['2021-01-05', '2021-07-05']
        
        >>> year_trans('前三年')
        ['2018-01-01', '2020-12-31']
        
        >>> year_trans('三年后')
        ['>=', '2024-07-09']
    """
    
    def infer_year(text) -> int:
        """ 一些特殊年份写法的推理
        """
        year = -1
        
        if '今年' in text or '现在' in text:
            year = this_year
        elif '去年' in text or '昨年' in text or '上一年' in text:
            year = this_year - 1                
        elif '前年' in text:
            year = this_year - 2
        elif '明年' in text:
            year = this_year + 1   
        elif '后年' in text:
            year = this_year + 2
        return year
        
    def year_completion(str_year: str) -> str:
        """将省略的年份补充为完整的年份
        
        2位年份小于40的认为是21世纪, 否则为是20世纪
        3位年份小于100的认为是21世纪, 否则认为是10世纪~20世纪
        
        Args:
            input (str): 阿拉伯数字表示的年份, 允许2位数字到4位数字
            
        Return:
            return (str): 补全后的年份
        
        Examples:
            >>> '08'
            '2008'
            
            >>> '207'
            '1207'
        """
        year_len = len(str_year)
        assert 2 <= year_len <= 4, f'数字年份长度不符合要求'
        if year_len == 2:
            num_year = int(str_year)
            res = '20' + str_year if num_year <=40 else '19' + str_year
            return res
        if year_len == 3:
            num_year = int(str_year)
            res = '2' + str_year if num_year <=100 else '1' + str_year
            return res
        if year_len == 4:
            return str_year
        return -1
    
    try:           
        # logger.debug(text)
        this_year = arrow.now().year

        ## -------------------------------- 隐含时间段 --------------------------------- ##
        # n年前
        rule = r'([0-9半一二两三四五六七八九十]+年)(前)'
        res = re.search(rule, text)
        if res:
            groups = res.groups()
            print(groups)
            # 半年前
            if groups[0] == '半年':
                month = arrow.now().shift(months=-6).format('YYYY-MM')
                st = month + '-01'
                ed = month + '-31'              
                return [st, ed]
            pure_num = number_translator(groups[0][:-1]) if groups[0] else 0
            # 3年前
            if len(pure_num) <= 3:
                year_ago = arrow.now().shift(years=-int(pure_num)).format('YYYY')
                year_st = year_ago + '-01-01'
                year_ed = year_ago + '-12-31'
                return [year_st, year_ed]
            # 2020年前
            if len(pure_num) == 4:
                return ['<=', str(int(pure_num)-1) + '-12-31']
                
        # n年后
        rule = r'([0-9半一二两三四五六七八九十]+年)(后)'
        res = re.search(rule, text)
        if res:
            groups = res.groups()
            print(groups)
            
            # 半年后
            if groups[0] == '半年':
                return ['>=', arrow.now().shift(months=+6).format('YYYY-MM-DD')]
            pure_num = number_translator(groups[0][:-1]) if groups[0] else 0
            # 3年后
            if len(pure_num) <= 3:
                return ['>=', arrow.now().shift(years=+int(pure_num)).format('YYYY-MM-DD')]
            # 2020年后
            if len(pure_num) == 4:
                return ['>=', str(pure_num) + '-01-01']
        
        # `最近`等的表述, 此处是从现在往前推, 含`半年`
        rule = r'(最近|近|过去)([0-9半一二两三四五六七八九十]+年)'
        res = re.search(rule, text)
        if res:
            res = res.groups()
            # print(res)
            if len(res) == 2:
                if res[1] == '半年':    
                    recent_st = arrow.now().shift(months=-6).format('YYYY-MM-DD')
                    recent_ed = arrow.now().format('YYYY-MM-DD')
                    return [recent_st, recent_ed]
                shift_year = int(number_translator(res[1][:-1]))
                recent_st = arrow.now().shift(years=-shift_year).format('YYYY-MM-DD')
                recent_ed = arrow.now().format('YYYY-MM-DD')
                return [recent_st, recent_ed]
            
        # `前3年`等的表述, 是去上一个年度的整年, 此处没有`半年`
        rule = r'(前)([0-9一二两三四五六七八九十]+年)'
        res = re.search(rule, text)
        # print(res)
        if res:
            res = res.groups()
            if len(res) == 2:
                shift_year = int(number_translator(res[1])[:-1])
                year_st = str(arrow.now().shift(years=-shift_year).year)
                year_ed = str(arrow.now().shift(years=-1).year)
                return [year_st + '-01-01', year_ed + '-12-31'] 

        ## --------------------------------- 指明年份 --------------------------------- ##
        # 有数字的和特殊年份等, 此种情况可以带`上半年` , `下半年`等
        rule = r"([0-9零一二两三四五六七八九十]{2,4})(年)"
        res = re.search(rule, text)
        # print(f'specific year: {res}')
        if res:
            res = res.groups()
            if res:
                str_year = number_translator(res[0])
                year = year_completion(str_year)
                # print(year)
                if '上半年' in text or '前半年' in text:
                    year = str(year) if year != -1 else str(this_year)
                    year_st = year + '-01-01'
                    year_ed = year + '-06-30'
                    return [year_st, year_ed]
                elif '下半年'in text or '后半年' in text:
                    year = str(year) if year != -1 else str(this_year)
                    year_st = year + '-07-01'
                    year_ed = year + '-12-31'
                    return [year_st, year_ed]
                else:
                    year_st = year + '-01-01'
                    year_ed = year + '-12-31'
                    return [year_st, year_ed]
                
        ## --------------------------------- 特殊年份 --------------------------------- ##
        # # 去年上半年, 下半年
        rule = r"([前|去|昨|今|明|后]年)*([上|下|前|后])*(半年)"
        res = re.search(rule, text)
        if res:
            res = res.groups()
            # print(res)
            if len(res) == 3 and res[0] is not None:
                year = str(infer_year(res[0]))
                if res[1] == '上' or res[1] == '前':
                    year_st = year + '-01-01'
                    year_ed = year + '-06-30'
                    return [year_st, year_ed]
                elif res[1] == '下' or res[1] == '后':
                    year_st = year + '-07-01'
                    year_ed = year + '-12-31'
                    return [year_st, year_ed]
            if len(res) == 3 and res[0] is None:
                year = str(this_year)
                # 半年: 默认为最近半年
                if not res[1]:  #
                    year_st = arrow.now().shift(months=-6).format('YYYY-MM-DD')
                    year_ed = arrow.now().format('YYYY-MM-DD')
                    return [year_st, year_ed]
                # 上半年
                if res[1] == '上' or res[1] == '前':
                    year_st = year + '-01-01'
                    year_ed = year + '-06-30'
                    return [year_st, year_ed]
                # 下半年
                elif res[1] == '下' or res[1] == '后':
                    year_st = year + '-07-01'
                    year_ed = year + '-12-31'
                    return [year_st, year_ed]
                
        # 去年, 明年
        rule = r"([前|去|昨|今|明|后]+)(年)"
        res = re.search(rule, text)
        if res:
            year = str(infer_year(text))
            return [year + '-01-01', year + '-12-31']
        return [] 
    
    except Exception:
        traceback.print_exc()
        return []


def season_trans(text: str, year_flag: bool = False) -> List:
    """季节的转换, 返回一个时间段 
    
    涉及到`近`和`最近`的不能直接按照当天推, 从上季度结束往前推
    此函数中, `春夏秋冬` 和 `一二三四` 季度等价

    Args:
        text (str): 输入文本
        year_flag (bool, optional): 季节前面是否有年份, 有的话在'前三个季度'这种处理会变为当
                                    年的前三季度. Defaults to False.
                                    
    Returns:
        List: 季度的开始和结束年月日
        
    Example: 
        >>> season_trans('前三个季度')
        ['2020-10-01', '2021-06-31']
        
        >>> season_trans('去年前三个季度')
        ['2020-01-01', '2020-09-30']
        
        >>> season_trans('春季')
        ['2021-01-01', '2021-03-31']
        
        >>> season_trans('上个季度')
        ['2021-04-01', '2021-06-31']
    """
    
    SEASON = {
        '1': ['01-01', '03-31'],
        '2': ['04-01', '06-30'],
        '3': ['07-01', '09-30'],
        '4': ['10-01', '12-31'],
    }
    
    def get_poem_season(text: str) -> List:
        """得到`春夏秋冬`的开始结束日期
        
        为了和第n季度保持一致, 这里约定春季1~3月, 夏季为4~6月, 秋季为7~9, 冬季为10~12月

        Args:
            text (str): 带季节的文字
            
        Returns:
            List: 季节的开始结束日期
        """
        this_year = arrow.now().format('YYYY')
        season = ['1', '1']
        if '春' in text:
            season = SEASON.get('1')
        elif '夏' in text:
            season = SEASON.get('2')
        elif '秋' in text:
            season = SEASON.get('3')
        elif '冬' in text:
            season = SEASON.get('4')
        season = [this_year + '-' + season[0], this_year + '-' + season[1]]
        return season
        
    def infer_month_by_season(season_num: int) -> List:
        """根据季节数往前推, 找到目标季节的开始结束日期
        
        Args:
            season_num (int): 往前推的季节数
            
        Returns:
            List: 季节的开始结束日期    
        """
        assert season_num >= 0, f'season_num < 0'
        year_shift = 0
        this_month = arrow.now().month
        his_year = arrow.now().format('YYYY')
        # 计算当前季度的开始月份
        if this_month <= 3:
            this_season_st = '01'
        elif this_month <= 6:
            this_season_st = '04'
        elif this_month <= 9:
            this_season_st = '07'
        elif this_month <= 12:
            this_season_st = '10'
            
        # 计算本季度
        if season_num == 0:
            start = this_year + '-' + this_season_st + '-01'
            month_end = int(this_season_st) + 2
            month_end = '0' + str(month_end) if month_end < 10 else str(month_end)
            end = this_year + '-' + month_end + '-31'
            return [start, end]     
        # 计算当前月和当前季节开始月的差距, 如六月, 差距为 6 - 4 = 2个月
        month_dist = this_month - int(this_season_st)
        # 月份偏移量
        month_shift = month_dist + season_num * 3
        # 目标开始年月
        year_st = arrow.now().shift(months=-month_shift).format('YYYY')
        month_st = arrow.now().shift(months=-month_shift).format('MM')
        # 目标结束年月
        year_ed = arrow.now().shift(months=-(month_dist+1)).format('YYYY')
        month_ed = arrow.now().shift(months=-(month_dist+1)).format('MM')
        start = year_st + '-' + month_st + '-01'
        end = year_ed + '-' + month_ed + '-31'
        return [start, end]
    
    try:
        # logger.debug(text)
        this_year = arrow.now().format('YYYY')
        
        poem_season_rule = r'[春夏秋冬]+[季天]+'
        common_num_season_rule = r'([0-9零一二两三四五六七八九十]+)(季|个季)'
                    
        # 春夏秋冬表明的季度
        poem_season_word = re.search(poem_season_rule, text)
        if poem_season_word:
            season_st, season_ed = get_poem_season(poem_season_word.group())
            return [season_st, season_ed]
        
        # 特殊字符: 这个季度
        this_season_rule = r'(本|这|这一|这1|当)+个*季'
        this_season_res = re.search(this_season_rule, text)
        if this_season_res:
            res = infer_month_by_season(0)
            return res
        
        # 特殊字符: 上个季度
        this_season_rule = r'(上|上个)+个*季'
        this_season_res = re.search(this_season_rule, text)
        if this_season_res:
            res = infer_month_by_season(1)
            return res
        
        # 数字表明的季度 
        season_num = re.search(common_num_season_rule, text)
        if season_num:
            season_number = number_translator(season_num.group())[0]
            this_month = arrow.now().month
            if season_number:
                # 特殊字符: 前n季度 前面带年
                year_flag_season_rule = r'(偂)([1-4一二两三四])+(季|个季)'
                year_flag_season_res = re.search(year_flag_season_rule, text)
                if year_flag and year_flag_season_res:
                    groups = year_flag_season_res.groups()
                    text_season_number = groups[1]
                    pure_season_num = number_translator(text_season_number)  # 只能是1,2,3,4
                    if pure_season_num in SEASON:
                        season_st = SEASON.get('1')[0]
                        season_ed = SEASON.get(pure_season_num)[1]
                        return [this_year + '-' + season_st, this_year + '-' + season_ed]

                # 特殊字符: 前|最近...|n季度
                #! 这里往前推可能会改变年份
                recent_season_rule = r'(最近|近|前|上|过去)+([0-9零一二两三四五六七八九十]*)(季|个季)'
                season_num_res = re.search(recent_season_rule, text)
                if season_num_res:
                    season_num_group = season_num_res.groups()
                    if len(season_num_group) == 3:
                        pure_season_num = season_num_group[1]
                        # 中间没有数字的, 默认为1
                        if pure_season_num == '':
                            res = infer_month_by_season(1)  
                        # 中间有数字的
                        else:
                            pure_season_num = number_translator(pure_season_num)
                            res = infer_month_by_season(int(pure_season_num))                        
                        return res
                # 纯数字
                season_st, season_ed = SEASON.get(season_number, [None, None])
                if season_st and season_ed:
                    return [this_year + '-' + season_st, this_year + '-' + season_ed]  
        return []
    
    except Exception:
        traceback.print_exc()
        return []


def month_trans(text: str, year_flag: bool = False) -> List:
    """月份的转换, 返回一个时间段 
    
    `最近3月`等词, 从当天往前推算3个月
    `前三月`等词, 计算本月之前三个完整月份
    
    `n月前`, n = {1, 2}, 返回本年度该月份前一个月的31号之前
    `n月后`, n = {1, 2}, 返回本年度该月份前一个月的1号之后
    
    `n个月前`, n = {1,2,3}, 返回当前时间往前推算n个月的整个月份
    `n个月后`, n = {1,2,3}, 返回当前时间往后推算n个月的1号

    Args:
        text (str): 输入文本
        year_flag (bool, optional): 月份前面是否有年份, 有的话在'前三个月'这种处理会变为当
                                    年的前三个月. Defaults to False.
                                    
    Returns:
        List: 月份的开始和结束年月日 
        
    Example:         
        >>> month_trans('本月')
        ['2021-07-01', '2021-07-31']
        
        >>> month_trans('最近三个月')
        ['2021-04-05', '2021-07-05']
        
        >>> month_trans('前三个月')
        ['2021-04-01', '2021-06-31']   
        
        >>> month_trans('四个月前')
        [('2021-03-01', '2021-03-31')]     
    """
    try:
        # logger.debug(text)
        
        this_year = arrow.now().format('YYYY')
        this_month = arrow.now().format('MM')
        
        this_month_rule = r'[本|这|当]+[1|一]*个*月'
        recent_month_num_rule = r'(最近|近)([0-9一二两三四五六七八九十]+)(月|个月)'
        before_month_num_rule = r'(过去|前|上)([0-9一二两三四五六七八九十]*)(月|个月)'
        several_month_before_rule = r'([0-9一二两三四五六七八九十]+)(个月)(前)'
        several_month_after_rule = r'([0-9一二两三四五六七八九十]+)(个月)(后)'
        specific_month_before_rule = r'([0-9一二两三四五六七八九十]{1,2})(月|月份)(前)'
        specific_month_after_rule = r'([0-9一二两三四五六七八九十]{1,2})(月|月份)(后)'
        year_flag_month_rule = r'(偂)([0-9一二两三四五六七八九十]+)(月|个月)'
        specific_month_num_rule = r'([0-9一二两三四五六七八九十]+)(月)'
        
        # 这个月 本月 ...
        this_month_res = re.search(this_month_rule, text)
        if this_month_res:
            month_st = this_year + '-' + this_month + '-01'
            month_ed = this_year + '-' + this_month + '-31'
            return [month_st, month_ed]
        
        # 最近几个月 #!可能跨过年份  从今天往前推
        recent_month_res = re.search(recent_month_num_rule, text)
        if recent_month_res:
            recent_month_group = recent_month_res.groups()
            if len(recent_month_group) == 3:
                pure_month_num = recent_month_group[1]                
                shift_month = int(number_translator(pure_month_num)) if pure_month_num else 1
                month_st = arrow.now().shift(months=-shift_month).format('YYYY-MM-DD')
                month_ed = arrow.now().format('YYYY-MM-DD')
                return [month_st, month_ed] 
            
        # n个月前/后
        several_month_before_res = re.search(several_month_before_rule, text)
        if several_month_before_res:
            groups = several_month_before_res.groups()
            shift_month = int(number_translator(groups[0]))
            month = arrow.now().shift(months=-shift_month).format('YYYY-MM')
            month_st = month + '-01'
            month_ed = month + '-31'
            return [month_st, month_ed]
        
        several_month_after_res = re.search(several_month_after_rule, text)
        if several_month_after_res:
            groups = several_month_after_res.groups()
            shift_month = int(number_translator(groups[0]))
            month_day = arrow.now().shift(months=+shift_month).format('YYYY-MM-DD')
            return ['>=', month_day]
           
        # n月前/后
        specific_month_before_res = re.search(specific_month_before_rule, text)
        if specific_month_before_res:
            groups = specific_month_before_res.groups()
            month = int(number_translator(groups[0]))
            if month == 1:
                return ['<=', str(int(this_year) - 1) + '-12-31']
            if 2 <= month <= 10:
                return ['<=', this_year + '-0' + str(month-1) + '-31']
            if 11 <= month <=12:
                return ['<=', this_year + '-' + str(month) + '-31']
            
        specific_month_after_res = re.search(specific_month_after_rule, text)
        if specific_month_after_res:
            groups = specific_month_after_res.groups()
            month = int(number_translator(groups[0]))
            if 1 <= month <= 9:
                return ['>=', this_year + '-0' + str(month) + '-01']
            if 10 <= month <= 12:
                return ['>=', this_year + '-' + str(month) + '-01']
            
        # 前n个月 前面带年
        year_flag_month_res = re.search(year_flag_month_rule, text)
        if year_flag and year_flag_month_res:
            groups = year_flag_month_res.groups()
            pure_month_num = groups[1]
            if pure_month_num:                
                month_num = int(number_translator(pure_month_num))
                if 1 <= month_num <= 12:
                    month_res = '0' + str(month_num) if month_num < 10 else str(month_num)
                    month_st = this_year + '-' + '01-01'
                    month_ed = this_year + '-' + month_res + '-31'
                    return [month_st, month_ed] 
            
        # 前几个月  #!可能跨过年份   从上个月末往前推
        before_month_res = re.search(before_month_num_rule, text)
        if before_month_res:
            before_month_group = before_month_res.groups()
            if len(before_month_group) == 3:
                pure_month_num = before_month_group[1]                
                shift_month = int(number_translator(pure_month_num)) if pure_month_num else 1
                month_st = arrow.now().shift(months=-shift_month).format('YYYY-MM') + '-01' 
                month_ed = arrow.now().shift(months=-1).format('YYYY-MM') + '-31' 
                return [month_st, month_ed] 

        # 具体数字月份
        specific_month_res =  re.search(specific_month_num_rule, text) 
        if specific_month_res:
            month_res = number_translator(specific_month_res.group())[:-1]
            month_res = '0' + month_res if len(month_res) == 1 else month_res
            month_st = this_year + '-' + month_res + '-01'
            month_ed = this_year + '-' + month_res + '-31'
            return [month_st, month_ed]
        return []
    
    except Exception:
        traceback.print_exc()
        return []


def week_trans(text: str) -> List:
    """周的转换, 返回一个时间段或时间点
    
    `最近一周`等词, 从当天往前推算一周
    `前三周`等词, 返回本周之前三个完整周
    
    `n周前`, 返回当前时间往前推算n周的整个周
    `n周后`, 返回大于当前时间往后推算n周的那天
        
    不支持`某月第三周` , `某月前三周`等词语, 因为周的开始点不易确定
    
    
    Args:
        text (str): 输入文本
                                    
    Returns:
        List: 日期 或 周的开始和结束年月日 
        
    Example:         
        >>> week_trans('周三')
        ['=', '2021-07-14']
        
        >>> week_trans('前三周')
        ['2021-06-21', '2021-07-11']
        
        >>> week_trans('三周前')
        ['2021-06-21', '2021-06-27']
        
        >>> week_trans('上周礼拜五')
        ['=', '2021-07-09']       
    """
    try:
        # logger.debug(text)
                
        # 先找到上周日, 再找到上上周日, 在它们的基础上做加减
        week_today = arrow.now().weekday()
        shift_day_from_last_sunday = week_today + 1
        last_sunday_arrow = arrow.now().shift(days=-shift_day_from_last_sunday)
        last_monday_arrow = last_sunday_arrow.shift(days=+1)
        last_2_sunday_arrow = last_sunday_arrow.shift(days=-7)
        
        # rule
        #! 前后顺序有关系, 匹配范围更大, 更一般的放后面
        recent_week_rule = r'(最近|近)([0-9一二两三四五六七八九十]+)(周)'
        before_week_rule = r'(过去|前)([0-9一二两三四五六七八九十]+)(周)'
        week_before_rule = r'([0-9一二两三四五六七八九十]+)(周前)'
        week_after_rule = r'([0-9一二两三四五六七八九十]+)(周后)'
        recent_weekday_rule = r'(上|上个|上一)+(周)+([1-7一二三四五六七])*'
        this_weekday_rule = r'(这|这个|本)*(周)+([1-7一二三四五六七])*'
        
        # 最近几周, 从今天开始往前推
        recent_week_res = re.search(recent_week_rule, text)
        if recent_week_res:
            groups = recent_week_res.groups()
            # print(groups)
            if len(groups) == 3:
                shift_num = int(number_translator(groups[1]))
                week_st = arrow.now().shift(weeks=-shift_num).format('YYYY-MM-DD')
                week_ed = arrow.now().format('YYYY-MM-DD')
                return [week_st, week_ed]
            
        # 前几周, 推到上一个周末
        before_week_res = re.search(before_week_rule, text)
        if before_week_res:        
            groups = before_week_res.groups()
            # print(groups)
            if len(groups) == 3:
                shift_num = int(number_translator(groups[1]))
                week_st = last_monday_arrow.shift(weeks=-shift_num).format('YYYY-MM-DD')
                week_ed = last_sunday_arrow.format('YYYY-MM-DD')
                return [week_st, week_ed]
            
        # n周前/后
        week_before_res = re.search(week_before_rule, text)
        if week_before_res:
            groups = week_before_res.groups()
            shift_week = int(number_translator(groups[0]))
            week_st = last_sunday_arrow.shift(weeks=-shift_week).shift(days=+1).format('YYYY-MM-DD')
            week_ed = last_sunday_arrow.shift(weeks=-(shift_week-1)).format('YYYY-MM-DD')
            return [week_st, week_ed]
        
        week_after_res = re.search(week_after_rule, text)
        if week_after_res:
            groups = week_after_res.groups()
            shift_week = int(number_translator(groups[0]))
            week_day = arrow.now().shift(weeks=+shift_week).format('YYYY-MM-DD')
            return ['>=', week_day]

        # 上周某天/上周
        recent_weekday_res = re.search(recent_weekday_rule, text)
        if recent_weekday_res:        
            groups = recent_weekday_res.groups()
            # print(groups)
            if len(groups) == 3:
                # 上周,上一周
                if not groups[2]:
                    week_st = last_2_sunday_arrow.shift(days=+1).format('YYYY-MM-DD')
                    week_ed = last_2_sunday_arrow.shift(days=+7).format('YYYY-MM-DD')
                    return [week_st, week_ed]
                # 上周二
                else:
                    shift_num = int(number_translator(groups[2]))
                    week_day = last_2_sunday_arrow.shift(days=+shift_num).format('YYYY-MM-DD')
                    return ['=', week_day]
                
        # 这周某天/这周
        this_weekday_res = re.search(this_weekday_rule, text)
        if this_weekday_res:        
            groups = this_weekday_res.groups()
            # print(groups)
            if len(groups) == 3:
                # 本周, 周
                if not groups[2]:
                    week_st = last_sunday_arrow.shift(days=+1).format('YYYY-MM-DD')
                    week_ed = last_sunday_arrow.shift(days=+7).format('YYYY-MM-DD')
                    return [week_st, week_ed]
                # 周三, 本周三
                else:
                    shift_num = int(number_translator(groups[2]))
                    week_day = last_sunday_arrow.shift(days=+shift_num).format('YYYY-MM-DD')
                return ['=', week_day]
        return []
    
    except Exception:
        traceback.print_exc()
        return []
    
      
def day_trans(text: str, month_flag: bool = False) -> List:
    """日期的转换, 返回一个时间段或时间点
    
    `最近n天`, `前n天` 等词, 均从当天往前推算到今天
    
    `n天前`, 返回等于当前时间往前推算n天的那天
    `n天后`, 返回大于当前时间往后推算n天的那天
    
    `n号/日前`, 返回小于当月n-1号的那天
    `n号/日后`, 返回大于当月n号的那天
    
    Args:
        text (str): 输入文本
        month_flag (bool, optional): 日期前面是否有月份, 有的话在'前20天'这种处理会
                                     变为当月的1-20天. Defaults to False.
                                    
    Returns:
        List: 日期 或 日期的开始和结束年月日 
        
    Example:         
        >>> day_trans('前五天')
        ['2021-07-08', '2021-07-13']
        
        >>> day_trans('十八日')
        ['=', '2021-07-18']
        
        >>> day_trans('五天前')
        ['=', '2021-07-08'] 
        
        >>> day_trans('五号之前')
        [('<=', '2021-07-04')]
    """
    
    SPECIAL_DAY = ['大前天', '前天', '昨天', '今天', '明天', '后天', '大后天']
    
    def special_day(text):
        res_day = -1
        today = arrow.now()
        if '前天' in text:
            res_day = today.shift(days=-2).format('YYYY-MM-DD')
        if '大前天' in text:
            res_day = today.shift(days=-3).format('YYYY-MM-DD')
        if '昨天' in text:
            res_day = today.shift(days=-1).format('YYYY-MM-DD')
        if '今天' in text:
            res_day = today.format('YYYY-MM-DD')
        if '明天' in text:
            res_day = today.shift(days=+1).format('YYYY-MM-DD')
        if '后天' in text:
            res_day = today.shift(days=+2).format('YYYY-MM-DD')  
        if '大后天' in text:
            res_day = today.shift(days=+3).format('YYYY-MM-DD')      
        return res_day
    
    try:
        # logger.debug(text)
    
        today_arrow = arrow.now()
        # rule
        recent_day_num_rule = r'(最近|近|前|这|过去)([0-9一二两三四五六七八九十]+)(天|日)'  # `+`放里面才能匹配'九十'天
        several_day_before_rule = r'([0-9一二两三四五六七八九十]+)(天)(前)'
        several_day_after_rule = r'([0-9一二两三四五六七八九十]+)(天)(后)'
        specific_day_before_rule = r'([0-9一二两三四五六七八九十]+)(号|日)(前)'
        specific_day_after_rule = r'([0-9一二两三四五六七八九十]+)(号|日)(后)'
        sepcial_day_rule = r'[前|昨|今|明|后]天'
        specific_day_num_rule = r'([0-9一二两三四五六七八九十]+)(号|日)'
        month_flag_day_rule = r'(偂)([0-9一二两三四五六七八九十]+)(天|日)'
        
        # 特殊字符: 昨天等
        for day in SPECIAL_DAY:
            if day in text:
                day_res = special_day(text)
                return ['=', day_res]
            
        # 特殊字符: 前n天, 前面有月份    
        month_flag_day_res = re.search(month_flag_day_rule, text)
        if month_flag and month_flag_day_res:
            groups = month_flag_day_res.groups()
            pure_day_num = groups[1]                
            if pure_day_num:
                pure_day_num = int(number_translator(pure_day_num))
                if 1 <= pure_day_num <= 31: # 此处用arrow.replace 可能会报错
                    day_st = today_arrow.replace(day=1).format('YYYY-MM-DD')
                    day_ed = today_arrow.replace(day=pure_day_num).format('YYYY-MM-DD')
                    return [day_st, day_ed] 
        
        # 特殊字符: 前n天
        recent_day_res = re.search(recent_day_num_rule, text)
        if recent_day_res:
            groups = recent_day_res.groups()
            if len(groups) == 3:
                pure_day_num = groups[1]                
                shift_day = int(number_translator(pure_day_num)) if pure_day_num else 1
                day_st = today_arrow.shift(days=-shift_day).format('YYYY-MM-DD')
                day_ed = today_arrow.format('YYYY-MM-DD')
                return [day_st, day_ed] 
            
        # n天前/后
        several_day_before_res = re.search(several_day_before_rule, text)
        if several_day_before_res:
            groups = several_day_before_res.groups()
            shift_day = int(number_translator(groups[0]))
            day = today_arrow.shift(days=-shift_day).format('YYYY-MM-DD')
            return ['=', day] 
            
        several_day_after_res = re.search(several_day_after_rule, text)
        if several_day_after_res:
            groups = several_day_after_res.groups()
            shift_day = int(number_translator(groups[0]))
            day = today_arrow.shift(days=+shift_day).format('YYYY-MM-DD')
            return ['>=', day] 
            
        #n号前/后
        specific_day_before_res = re.search(specific_day_before_rule, text)
        if specific_day_before_res:
            groups = specific_day_before_res.groups()
            day_num = int(number_translator(groups[0]))
            if day_num == 1:
                day = today_arrow.shift(months=-1).format('YYYY-MM') + '-31'
                return ['<=', day] 
            if 2 <= day_num <= 32:
                str_day = str(day_num - 1)
                str_day = '0' + str_day if len(str_day) == 1 else str_day
                day = today_arrow.format('YYYY-MM') + '-' + str_day
                return ['<=', day] 
        
        specific_day_after_res = re.search(specific_day_after_rule, text)
        if specific_day_after_res:
            groups = specific_day_after_res.groups()
            day_num = int(number_translator(groups[0]))
            if 1 <= day_num <= 31:
                str_day = '0' + str(day_num) if day_num < 10 else str(day_num)
                return ['>=', today_arrow.format('YYYY-MM') + '-' + str_day]
    
        # 具体天
        specific_day_res = re.search(specific_day_num_rule, text)
        if specific_day_res:
            groups = specific_day_res.groups()
            day_num = int(number_translator(groups[0]))
            day_res = today_arrow.replace(day=day_num).format('YYYY-MM-DD')
            return ['=', day_res]
        return []
    
    except Exception:
        traceback.print_exc()
        return []
    

def text_preprocess(text: str) -> str:
    """一些字符串的前处理, 包括词语的转换和一些省略说法的补全

    Args:
        text (str): 转化前的字符串

    Returns:
        str: 转化后的字符串
    
    Examples:
        >>> text_preprocess('礼拜天')
        '周七'
        
        >>> text_preprocess('六月2到3号')
        '六月2号到3号'
        
        >>> text_preprocess('08年五到六月')
        '08年五月到六月'
    """    

    # 词语转换
    week_rule = r'星期|礼拜'
    weekend_rule = r'周日|周末|周天'
    text = re.sub(week_rule, '周', text)
    text = re.sub(weekend_rule, '周七', text)
    text = text.replace('至', '到')
    text = text.replace('到期', '过期')
    text = text.replace('之内', '内')
    text = text.replace('之前', '前')
    text = text.replace('以前', '前')
    text = text.replace('之后', '后')
    text = text.replace('以后', '后')
    # 单独的`现在`转为空, 时间段的`现在`不变
    if '现在' in text and '到' not in text:
        text = text.replace('现在', 'now')
    text = text.replace('现在', '今天')
    
    # -------------------------------  `内`的转化  --------------------------------# 
    year_in_rule = r'([0-9半一二两三四五六七八九十]+)(年)(内)'
    res = re.search(year_in_rule, text)
    if res:
        groups = res.groups()
        if groups[0] and groups[1] and groups[2]:
            old = groups[0] + groups[1] + groups[2]
            new = '最近' + groups[0] + groups[1] 
            text = text.replace(old, new) 
            
    season_in_rule = r'([0-9一二两三四五六七八九十]+)(个季节|个季度)(内)'
    res = re.search(season_in_rule, text)
    if res:
        groups = res.groups()
        if groups[0] and groups[1] and groups[2]:
            old = groups[0] + groups[1] + groups[2]
            new = '最近' + groups[0] + groups[1] 
            text = text.replace(old, new) 
            
    month_in_rule = r'([0-9一二两三四五六七八九十]+)(个月)(内)'
    res = re.search(month_in_rule, text)
    if res:
        groups = res.groups()
        if groups[0] and groups[1] and groups[2]:
            old = groups[0] + groups[1] + groups[2]
            new = '最近' + groups[0] + groups[1] 
            text = text.replace(old, new) 
            
    week_in_rule = r'([0-9一二两三四五六七八九十]+)(周|个周)(内)'
    res = re.search(week_in_rule, text)
    if res:
        groups = res.groups()
        if groups[0] and groups[1] and groups[2]:
            old = groups[0] + groups[1] + groups[2]
            new = '最近' + groups[0] + groups[1] 
            text = text.replace(old, new) 
            
    day_in_rule = r'([0-9一二两三四五六七八九十]+)(天|日)(内)'
    res = re.search(day_in_rule, text)
    if res:
        groups = res.groups()
        if groups[0] and groups[1] and groups[2]:
            old = groups[0] + groups[1] + groups[2]
            new = '最近' + groups[0] + groups[1] 
            text = text.replace(old, new) 
                
    # ---------------------`前`的转化, 以区别`三月前`和`三月前三天` --------------------# 
    if '年前' in text:
        year_before_rule = r'[0-9一二两三四五六七八九十]+(个季|季|月|个月)'
        res = re.search(year_before_rule, text)
        if res:
            text = text.replace('年前', '年偂')  
            
    if '月前' in text:
        month_before_rule = r'[0-9一二两三四五六七八九十]+(天|日)'
        res = re.search(month_before_rule, text)
        if res:
            text = text.replace('月前', '月偂')
        
    
    # 省略补全, 只针对`到`, `和`的情况    
    # if text.count('到') == 1 or text.count('和') == 1: 
    if '到' in text or '和' in text: 
        # ------------------------------ 后面补齐前面 ------------------------------#
        # 年
        com_rule = r'([0-9零一二两三四五六七八九十]+)(到|和)+(\S+年)'
        com_res = re.search(com_rule, text)
        if com_res:
            old = com_res.groups()[0]
            text = text.replace(old, old + '年')
            
        # 季度
        com_rule = r'([1-4一二三四]+)(到|和)+(\S+季)'
        com_res = re.search(com_rule, text)
        if com_res:
            old = com_res.groups()[0]
            text = text.replace(old, old + '季')
       
        # 月份 
        com_rule = r'([0-9零一二两三四五六七八九十]+)(到|和)+(\S+月)'
        com_res = re.search(com_rule, text)
        if com_res:
            old = com_res.groups()[0]
            text = text.replace(old, old + '月')
            
        # 日
        com_rule = r'([0-9零一二两三四五六七八九十]+)(到|和)+(\S+[日号天])'
        com_res = re.search(com_rule, text)
        if com_res:
            old = com_res.groups()[0]
            text = text.replace(old, old + '号')
            
        # ------------------------------ 前面补齐后面 ------------------------------#
        # 年/季度
        com_rule = r'([0-9去今明零一二两三四五六七八九十]+年)(第*[1-4一二三四春夏秋冬]+个*)(季节|季度|季)(到|和)(第*[1-4一二三四春夏秋冬]+个*)(季节|季度|季)'
        com_res = re.search(com_rule, text)
        if com_res:
            groups = com_res.groups()  
            old = groups[4]
            text = text.replace(old,  groups[0] + old)
            
        # 年/月
        com_rule = r'([0-9去今明零一二两三四五六七八九十]+年)(第*[0-9一二两三四五六七八九十]+)(月|个月|月份)(到|和)+(第*[0-9一二两三四五六七八九十]+)(月|个月|月份)'
        com_res = re.search(com_rule, text)
        if com_res:
            old = com_res.groups()[4] + com_res.groups()[5]
            text = text.replace(old, com_res.groups()[0] + old)
            
        # 年月日
        com_rule = r'([0-9去今明零一二两三四五六七八九十]+年)*([0-9一二两三四五六七八九十]+月)([0-9一二两三四五六七八九十]+[号|日])(到|和)([0-9零一二两三四五六七八九十]+年)*([0-9一二两三四五六七八九十]+月)*([0-9一二两三四五六七八九十]+[号|日])'
        com_res = re.search(com_rule, text)
        if com_res:
            groups = com_res.groups()  # (None, '3月', '5日', '到', None, None, '7日')
            l_year = groups[0]
            l_month = groups[1]
            l_day = groups[2]
            r_year = groups[4]
            r_month = groups[5]
            r_day = groups[6]
            # 月日 到 日
            if (l_month and l_day and r_day) and not (l_year or r_year or r_month):
                old = r_day
                text = text.replace(old, l_month + old)
            # 年月日 到 月日
            if (l_year and l_month and l_day and r_month and r_day) and not r_year:
                old = r_month + r_day
                text = text.replace(old, l_year + old)
            # 年月日 到 日
            if (l_year and l_month and l_day and r_day) and not (r_year or r_month):
                old = r_day
                text = text.replace(old,  l_year + l_month + old)
                
        com_rule = r'(上周|下周)([1-7一二三四五六七]+)(到)(周)([1-7一二三四五六七]+)'
        com_res = re.search(com_rule, text)
        if com_res:
            old = com_res.groups()[3] + com_res.groups()[4]
            text = text.replace(old, com_res.groups()[0] + com_res.groups()[4])
    return text


def get_legal_output(date: List) -> List:
    """组织合理的返回结构, 并将一些不合规则的输入返回[]
    
    Args:
        date (List): 原始结果列表

    Returns:
        List: 过滤后的列表
        
    Examples:
        >>> get_legal_output(['2018-09-18', '2017-09-18'])
        []
        
        >>> get_legal_output(['>=', '2018-9-18])
        []
        
        >>> get_legal_output(['2018-09-18', '2021-09-16'])
        [('2018-09-18', '2021-09-16')]
    """
    def is_leap_year(year: int) -> bool:
        """闰年判断
        """
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return True
        return False
        
    
    def date_correct(date_str: str) -> str:
        """对具体月份日期的纠正, 考虑闰年的情况
        Args:
            date_str (str): 输入的年月日
        
        Returns:
            str: 纠正后的日期年月日
        """
        # logger.debug(f'{date_str}')
        year, month, day = date_str.split('-')
        if int(day) >= 31 and month in SMALL_MONTH:
            return date_str[:-2] + '30'
        if month == '02' and int(day) >= 29:
            if is_leap_year(int(year)):
                return date_str[:-2] + '29'
            return date_str[:-2] + '28'
        return date_str
            
            
    def is_start_smaller(start: str, end: str) -> bool:
        """判断开始日期是否比结束日期小

        Args:
            start (str): 开始日期
            end (str): 结束日期

        Returns:
            bool
        """
        year_st, month_st, day_st = start.split('-')
        year_ed, month_ed, day_ed = end.split('-')
        # 年份小, 满足
        if int(year_st) < int(year_ed):
            return True
        # 年份相等, 比月份
        if int(year_st) == int(year_ed):
            # 月份小, 满足
            if int(month_st) < int(month_ed):
                return True
            # 月份相等, 比日期
            if int(month_st) == int(month_ed):
                return True if int(day_st) <= int(day_ed) else False
            # 月份大, 不满足
            return False
        # 年份大, 不满足
        return False
        
    # 长度判断
    if len(date) != 2:
        # logger.debug(f'结果列表不是标准长度: {date}')
        return []

    ## ------------------------- 时间点, ['<=', 'YYYY-MM-DD'] --------------------- ##
    if date[0] in OP:
        if len(date[1]) != 10:
            # logger.debug(f'结果不是标准长度: {date}')
            return []
        date[1] = date_correct(date[1])
        return [tuple(date)]
    
    ## ---------------------- 时间段, ['YYYY-MM-DD', 'YYYY-MM-DD'] ---------------- ##
    st = date[0]
    ed = date[1]
    # 判断长度是否合法
    if len(st) != 10 or len(ed) != 10:
        # logger.debug(f'结果不是标准长度: {date}')
        return []
    # 判断日期大小是否合法
    if not is_start_smaller(st, ed):
        # logger.debug(f'结果不符合常识: {date}')
        return []
    # 纠正各个月份的日期
    date[0] = date_correct(st)
    date[1] = date_correct(ed)
    return [tuple(date)]

        
def combine_result(total_groups: Tuple) -> List:
    """组织各个函数的结果, 以天为粒度返回结果时间点或者时间段

    Args:
        total_groups (Tuple): 通过全部规则搜索后的分组

    Returns:
        List: 时间点或者时间段, 没有符合的则返回空列表
    """
    try:
        # logger.debug(f'{total_groups}')
        ## ------------------------ 每个子函数的结果 -------------------------##
        # 年
        year = year_trans(total_groups[0]) if total_groups[0] else None
        # 季
        if total_groups[1]:
            season = season_trans(total_groups[1], year_flag=1) if total_groups[0] else season_trans(total_groups[1])
        else:
            season = None
        # 月
        if total_groups[2]:
            month = month_trans(total_groups[2], year_flag=1) if total_groups[0] else month_trans(total_groups[2])
        else:
            month = None    
        # 周
        week = week_trans(total_groups[3]) if total_groups[3] else None
        # 日
        if total_groups[4]:
            day = day_trans(total_groups[4], month_flag=1) if total_groups[2] else day_trans(total_groups[4])
        else:
            day = None
        
        ## ------------------------ 结果的组合逻辑 -------------------------##
        # 只有年            
        if year and not (season or month or week or day):
            return year
        # 只有季
        if season and not (year or month or week or day):
            return season
        # 只有月
        if month and not (year or season or week or day):
            return month 
        # 只有周
        if week and not (year or season or month or day):
            return week 
        # 只有天
        if day and not (year or season or month or week):
            return day 
        
        # 年/季节, 都是时间段
        if (year and season) and not (month or week or day):
            res_year = year[0].split('-')[0]    
            return [res_year + season[0][4:], res_year + season[1][4:]]
        
        # 年/月, 都是时间段
        if (year and month) and not (season or week or day):
            res_year = year[0].split('-')[0]
            if month[0] in OP:
                # 2019年1月前这种的特殊处理, 年份-1
                if month[0] == '<=' and month[1][-6:] == '-12-31':
                    return [month[0], str(int(res_year) - 1) + month[1][4:]]
                return [month[0], res_year + month[1][4:]]
            return [res_year + month[0][4:], res_year + month[1][4:]]
        
        # 月/日, 月是时间段, 日是{时间点, 时间段}
        if (month and day) and not (year or season or week):
            # 7月30日, 返回的是时间点
            if day[0] in OP:
                # 1号之前的处理
                if day[1][-2:] == '31' and day[0] == '<=':
                    # 1月1日, 年份-1, 月份=12
                    if month[0][5:7] == '01':
                        year_res = str(int(month[0][:4]) - 1)
                        month_res = '12'
                        return [day[0], year_res + '-' + month_res + '-31']
                    # 4月1日的特殊处理, 月份-1
                    month_res = str(int(month[0][5:7]) - 1)
                    month_res = '0' + month_res if len(month_res) == 1 else month_res
                    return [day[0], month[0][0:5] + month_res + '-31']
                return [day[0], month[0][:-3] + day[1][-3:]]
            
            # 7月前30日, 返回的是时间段
            return [month[0][:-3] + day[0][-3:], month[0][:-3] + day[1][-3:]]
        
        
        # 年/月/日 , 年月是时间段, 日是时间点
        if (year and month and day) and not (season or week):
            if day[0] in OP:
                res_year = year[0].split('-')[0]
                res_month = month[0].split('-')[1]
                res_day = day[1].split('-')[2]
                return [day[0], res_year + '-' + res_month + '-' + res_day]
        return []
    
    except Exception:
        traceback.print_exc()
        return []


def cdt(text: str) -> List:
    """将中文的日期转化为标准时间日期符串
    
    支持年, 季, 月, 周, 日,以及他们的合理组合, 返回的粒度都为`日`
    支持日期合理的往前推算, 如`去年第一季度`, `前20天`等
    支持两位数和三位数年份的自动补全. 如`18年`, '95年'等
    
    Args:
        text (str): 输入文本
    
    Returns:
        List: 转化过后的时间, `和`表示的长度为2, 正常的长度为1, 不能转化或者转化出错返回空列表
        
    Examples:
        >>> cdt('上三')
        []
    
        >>> cdt('上周三')
        [('=', '2021-07-01')]
        
        >>> cdt('2018年前三季度')
        [('2018-01-01', '2018-09-31')]
        
        >>> cdt('18年4月十号到二零二零年5月4日')
        [('2018-04-10', '2020-05-04')]
        
        >>> cdt('18年4月十号和二零二零年5月4日')
        [('=', '2018-04-10'), ('=', '2020-05-04')]
        
        >>> cdt('张飞和关羽三月份和七月份的饭量')
        [('2021-03-01', '2021-03-31'), ('2021-07-01', '2021-07-31')]
    """
    try:
        text = text_preprocess(text)
        # logger.debug(f'after text_preprocess: {text}')
        total_rule = r"(\S+年前*后*)?(\S+季前*后*)?(\S+月份*前*后*)?(\S*[0-9一二两三四五六七八九十]*周前*后*[1-7一二三四五六七]*)?(\S+[0-9一二两三四五六七八九十]*[号日天]前*后*)?"
        
        # ---------------------- 到, res = [('YYYY-MM-DD, YYYY-MM-DD')] ---------------- #
        if '到' in text:
            split_list = text.split('到')
            # logger.debug(f'根据`到`分割后的列表: {split_list}')
            until_flag = False
            # 找到匹配的时间就返回
            for idx in range(len(split_list) - 1):
                time_st = split_list[idx]
                time_ed = split_list[idx+1]
                time_st_find = re.search(total_rule, time_st)
                time_ed_find = re.search(total_rule, time_ed)
                st_groups = time_st_find.groups()
                ed_groups = time_ed_find.groups()
                # 排除普通的`和`的情况
                if any(st_groups) and any(ed_groups):
                    until_flag = True
                    break
            if until_flag == True:
                st_res = combine_result(st_groups)
                ed_res = combine_result(ed_groups)
                # 前面是时间点
                if st_res[0] in OP:
                    res = [st_res[1], ed_res[1]]
                    return get_legal_output(res)
                # 前面是时间段
                if st_res[0] not in OP:
                    res = [st_res[0], ed_res[1]]
                    return get_legal_output(res)
                    
        # ---- 和, res = [('YYYY-MM-DD, YYYY-MM-DD'), ('YYYY-MM-DD', 'YYYY-MM-DD')] --- #
        if '和' in text:
            split_list = text.split('和')
            # logger.debug(f'根据`和`分割后的列表: {split_list}')
            and_flag = False
            # 找到匹配的时间就返回
            for idx in range(len(split_list) - 1):
                time_st = split_list[idx]
                time_ed = split_list[idx+1]
                time_st_find = re.search(total_rule, time_st)
                time_ed_find = re.search(total_rule, time_ed)
                st_groups = time_st_find.groups()
                ed_groups = time_ed_find.groups()
                # 排除一般的`和`的情况
                if any(st_groups) and any(ed_groups):
                    and_flag = True
                    break
            if and_flag:
                st_res = combine_result(st_groups)
                ed_res = combine_result(ed_groups)
                # 将两个时间合并起来
                res1 = get_legal_output(st_res)
                res2 = get_legal_output(ed_res)
                if res1 and res2:
                    res1.extend(res2)
                    return res1
        
        # ------------------- 一般情况, res = [('YYYY-MM-DD, YYYY-MM-DD')] ------------- #
        time_find = re.search(total_rule, text)
        groups = time_find.groups()
        # 一般情况
        if any(groups):
            res = combine_result(groups)
            return get_legal_output(res)
        # `最近`没有指明时间, 默认为`最近10天`
        if '最近' in text:
            return cdt('最近10天')
        return []
    
    except Exception:
        traceback.print_exc()
        return []

   
if __name__ == '__main__':
    
    # 一些测试的例子 
    texts = [
        #! union
        # '2019年4月10日',
        # '2019年4月10日到2020年5月16日',
        # '2018年到2019年',
        # '第1季度到第四季度',
        # '2018年第2季度到2021年第三季度',
        # '18年4月到二零二零年5月',
        # '4月19号到十二月7日',
        
        # '14年十二月八号至19年4月29日',
        # '18年4月十号到二零二零年5月4日',
        # '昨天到今天到明天',
        # '2019年到18年',
        # '95年到14年',
        # '98年和14年',
        # '2000年第一季度',
        # '2018年4月',
        # '6月十五号',
        
        # '2016年十月三十号',
        # '上周末',
        # '2018年前两个季度',
        # '前三季度',
        # '20年前2个月',
        # '前三个月',
        # '95年第一季度',
        # '08年第一场雪',
        # '2017年3月到6月',
        # '2018年第一季度到第三季度',

        #!  year
        # '一九年上半年',
        # '最近半年的天气咋样?',
        # '上半年',
        # '去年下半年',
        # '最近三年',
        # '前三年',
        # '5年前',
        # '5年后',
        # '5年内',

        #! season
        # '这个季度',
        # '第三季',
        # '最近1个季度',
        # '上个季度',
        # '前三个季度',
        # '去年前三个季度',
        # '这1季',
        
        #! month
        # '近三个月',
        # '这个月',
        # '本月',
        # '前三个月',
        # '五月份',
        # '4月前',
        # '4个月前',
        # '5月份以后',
        # '5个月后',
        # '去年5月前',
        # '一个月',
        
        #! week
        # '这一周',
        # '周三',
        # '这周',
        # '这周五',
        # '最近一周',
        # '前1周',
        # '上周礼拜五',
        # '上礼拜三到这星期五',
        # '上周周一到周四',
        # '三周前',
        # '前三周',
        # '三周后',
                        
        #! day
        # '今天',
        # '2号到今天',
        # '2号到30号',
        # '前五天',
        # '十八日',
        # '五天前',
        # '五号前',
        # '30号',
        # '五月一号到三号',
        # '五月前十天',
        # '3天后',
        # '5月3号前',
        # '1月1日前',
        # '十五号到昨天',

        #! 到
        # '6月到七月',
        # '18年6月1号到30号',
        # '19年第一季度到第二季度',
        # '去年到今天',
        # '去年到今年',
        # '去年一月一号到2021年7月13日',
        # '去年1月1号到今年',
        # '去年到现在',
        
        #! 和
        # '2019年八月1日和十月20日',
        # '2015年4月和去年3月',
        # '1号和5号',
        # '2019年和今年',
        # '张飞和关羽四月份的体重',
        # '张飞和关羽三月份和七月份的饭量',
        # '张飞和关羽去年三月到六月的运动量',
        # '第一季度',
        
        #! 最近
        # '最近销量咋样啊',
        # '最近3天去哪儿玩了',
        
        #! 现在
        '今天房价如何?',
        '这个人现在是这么状态?',
        '现在在哪?',
    ]
    
    for text in texts:
        res = cdt(text)
        print(f'{res}')
        print('-' * 100)
