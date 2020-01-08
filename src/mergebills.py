import os
from os.path import *
from src.category import *


def load_category():
    result_dict = {}
    for cat1, cat2_and_item in counterparty_category.items():
        for cat2, items in cat2_and_item.items():
            for item in items:
                result_dict[item] = {'category1': cat1, 'category2': cat2}
    return result_dict


def load_bills_zfb(input_file_zfb):
    header = None
    contents = []
    result_list = []
    name = basename(input_file_zfb).split('_')[0]
    if name not in {'高飞龙', '姜斯茵'}:
        raise Exception('不能识别的姓名: ', name)

    with open(input_file_zfb) as file_zfb:
        for line in file_zfb:
            if line.startswith('交易号'):
                header = [h.strip() for h in line.split(',')[:-1]]
            elif line.startswith('2019') or line.startswith('202'):
                contents.append([item.strip() for item in line.split(',')[:-1]])
            else:
                # print('不能识别的内容: ', line)
                pass

    category_dict = load_category()
    for item in contents:
        new_item = dict(zip(['姓名', '支付通道'] + header, [name, '支付宝'] + item))
        if new_item['交易对方'].startswith('友宝售货机'):
            new_item['交易对方'] = '友宝售货机'
        if new_item['交易对方'] in category_dict:
            new_item['主类别'] = category_dict[new_item['交易对方']]['category1']
            new_item['子类别'] = category_dict[new_item['交易对方']]['category2']
        elif new_item['交易来源地'] == '淘宝':
            new_item['主类别'] = '网购'
            new_item['子类别'] = '淘宝天猫'
        else:
            if '餐' in new_item['交易对方'] or '餐' in new_item['商品名称']:
                new_item['主类别'] = '餐饮日用'
                new_item['子类别'] = '餐饮'
            else:
                new_item['主类别'] = '餐饮日用'
                new_item['子类别'] = '未分类消费'
        result_list.append(new_item)
    # print(result_list)
    return result_list


def load_bills_wx(input_dir_wx):
    header = None
    contents = []
    result_list = []
    name = basename(input_dir_wx).split('_')[0]
    if name not in {'高飞龙', '姜斯茵'}:
        raise Exception('不能识别的姓名: ', name)

    input_files = [root + '/' + files[0] for root, dirs, files in os.walk(input_dir_wx) if len(files) != 0]
    for input_file in input_files:
        with open(input_file, encoding='utf8') as file:
            for line in file:
                if line.startswith('交易时间'):
                    header = [h.strip() for h in line.split(',')[:-1]]
                elif line.startswith('20') and len(line.split(',')[0]) == 19:
                    contents.append([item.strip() for item in line.split(',')[:-1]])
                else:
                    # print('不能识别的内容: ', line)
                    pass

    category_dict = load_category()
    for item in contents:
        new_item = dict(zip(['姓名', '支付通道'] + header, [name, '微信'] + item))
        new_item['商品'] = new_item['商品'].strip('"')
        new_item['金额(元)'] = new_item['金额(元)'].strip('¥')
        if new_item['交易对方'] in category_dict:
            new_item['主类别'] = category_dict[new_item['交易对方']]['category1']
            new_item['子类别'] = category_dict[new_item['交易对方']]['category2']
        else:
            if '餐' in new_item['交易对方'] or '餐' in new_item['商品']:
                new_item['主类别'] = '餐饮日用'
                new_item['子类别'] = '餐饮'
            else:
                new_item['主类别'] = '餐饮日用'
                new_item['子类别'] = '未分类消费'
        if new_item['交易对方'] == '/':
            new_item['主类别'] = '红包'
            new_item['子类别'] = '红包'
        result_list.append(new_item)
    return result_list


def select_common_columns(bill_list):
    header = bill_list[0].keys()
    result_list = []
    if '交易来源地' in header:
        # 支付宝
        for item in bill_list:
            result_list.append([item[h] for h in header_zfb_in_common.keys()])
        return [dict(zip(header_zfb_in_common.values(), item)) for item in result_list]
    elif '商户单号' in header:
        # 微信
        for item in bill_list:
            result_list.append([item[h] for h in header_wx_in_common.keys()])
        return [dict(zip(header_wx_in_common.values(), item)) for item in result_list]
    else:
        raise Exception('无法识别的账单类型：', header)


def write_as_csv(bill_list, filename):
    if not exists(dirname(filename)):
        os.makedirs(dirname(filename))
    with open(filename, 'w', encoding='gb18030') as file:
        file.write(','.join(bill_list[0].keys()) + '\n')
        for item in bill_list:
            file.write(','.join(item.values()) + '\n')


def merge_zfb(input_file_zfb_gfl, input_file_zfb_jsy, output_file_zfb):
    bill_list_zfb_gfl = load_bills_zfb(input_file_zfb_gfl)
    bill_list_zfb_jsy = load_bills_zfb(input_file_zfb_jsy)
    write_as_csv(bill_list_zfb_gfl + bill_list_zfb_jsy, output_file_zfb)


def merge_wx(input_dir_wx_gfl, input_dir_wx_jsy, output_file_wx):
    bill_list_wx_gfl = load_bills_wx(input_dir_wx_gfl)
    bill_list_wx_jsy = load_bills_wx(input_dir_wx_jsy)
    write_as_csv(bill_list_wx_gfl + bill_list_wx_jsy, output_file_wx)


def merge_gfl(input_file_zfb_gfl, input_dir_wx_gfl, output_file_gfl):
    bill_list_zfb_gfl = select_common_columns(load_bills_zfb(input_file_zfb_gfl))
    bill_list_wx_gfl = select_common_columns(load_bills_wx(input_dir_wx_gfl))
    write_as_csv(bill_list_wx_gfl + bill_list_zfb_gfl, output_file_gfl)


def merge_jsy(input_file_zfb_jsy, input_dir_wx_jsy, output_file_jsy):
    bill_list_zfb_jsy = select_common_columns(load_bills_zfb(input_file_zfb_jsy))
    bill_list_wx_jsy = select_common_columns(load_bills_wx(input_dir_wx_jsy))
    write_as_csv(bill_list_wx_jsy + bill_list_zfb_jsy, output_file_jsy)


def merge_all(input_file_zfb_gfl, input_dir_wx_gfl, input_file_zfb_jsy, input_dir_wx_jsy, output_file_all):
    bill_list_zfb_gfl = select_common_columns(load_bills_zfb(input_file_zfb_gfl))
    bill_list_wx_gfl = select_common_columns(load_bills_wx(input_dir_wx_gfl))
    bill_list_zfb_jsy = select_common_columns(load_bills_zfb(input_file_zfb_jsy))
    bill_list_wx_jsy = select_common_columns(load_bills_wx(input_dir_wx_jsy))

    result_list = []
    for item in bill_list_zfb_gfl + bill_list_wx_gfl + bill_list_zfb_jsy + bill_list_wx_jsy:
        if item['收支'] == '支出' and \
                item['交易对方'] not in free_charge_counterparty and \
                not item['订单ID'] in free_charge_trade_id and \
                item['交易状态'] in {'支付成功', '交易成功'}:
            result_list.append(item)
    write_as_csv(result_list, output_file_all)


if __name__ == '__main__':
    print('start...')
    date_range = '20190101_20200109'
    input_file_zfb_gfl = '../bills/支付宝/高飞龙_支付宝_{}.csv'.format(date_range)
    input_dir_wx_gfl   = '../bills/微信/高飞龙_微信_{}'.format(date_range)
    input_file_zfb_jsy = '../bills/支付宝/姜斯茵_支付宝_{}.csv'.format(date_range)
    input_dir_wx_jsy   = '../bills/微信/姜斯茵_微信_{}'.format(date_range)
    output_file_zfb    = '../output/支付宝/支付宝_全部.csv'
    output_file_wx     = '../output/微信/微信_全部.csv'
    output_file_gfl    = '../output/高飞龙/高飞龙_全部.csv'
    output_file_jsy    = '../output/姜斯茵/姜斯茵_全部.csv'
    output_file_all    = '../output/全部/全部.csv'
    # 合并
    merge_zfb(input_file_zfb_gfl, input_file_zfb_jsy, output_file_zfb)
    merge_wx(input_dir_wx_gfl, input_dir_wx_jsy, output_file_wx)
    merge_gfl(input_file_zfb_gfl, input_dir_wx_gfl, output_file_gfl)
    merge_jsy(input_file_zfb_jsy, input_dir_wx_jsy, output_file_jsy)
    merge_all(input_file_zfb_gfl, input_dir_wx_gfl, input_file_zfb_jsy, input_dir_wx_jsy, output_file_all)
    print('done!!!')
