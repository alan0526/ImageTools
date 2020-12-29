from ui.customwidget import SubWindow
from tools.pqtools_to_code.pqtools2code_window import Ui_PQtoolsToCode
import xml.dom.minidom as xmldom
import os
import time
from PySide2.QtWidgets import QFileDialog


class PQtoolsParams:
    tab_space = 4
    max_line_char_counts = 120
    xmlfile = ''
    product_id = 'imx415'
    output_path = ''
    author = 'liqinxing'
    filter_struct = """hiISP_SHARPEN_ATTR_S
customNRX_PARAM_AUTO_V1_S
hiNRX_PARAM_MANUAL_V1_S
hiVPSS_GRP_SHARPEN_ATTR_S
hiISP_NR_ATTR_S
hiISP_ANTIFALSECOLOR_ATTR_S
hiISP_DEMOSAIC_ATTR_S
hiISP_CR_ATTR_S
hiISP_LDCI_ATTR_S
"""
    custom_define_dict = """typedef struct customNRX_PARAM_AUTO_V1_S {
    HI_U32 u32ParamNum;
    HI_U32 ATTRIBUTE au32ISO[16];
    VI_PIPE_NRX_PARAM_V1_S ATTRIBUTE pastNRXParamV1[16];
} CUSTOM_NRX_PARAM_AUTO_V1_S;
"""
    need_remove_item = 'rb'
    is_const = True
    include_headers = """# include "mpi_isp.h"
# include "mpi_vi.h"
# include "mpi_vpss.h"
# include "hi_comm_vi.h"
# include "hi_comm_vpss.h"
# include "hi_isp_defines.h"
"""
    add_custom_defines = """hiNRX_PARAM_AUTO_V1_S:customNRX_PARAM_AUTO_V1_S"""
    copyright = """/*
* Copyright (c) 2020
* All rights reserved.
*
* Description: image isp params head file
* Author: liqinxing
* Create: 2020-12-28
* Modefication History:
* Author: %AUTHOR%
* Date: %NOW_TINE%
*/
"""

    def get_params(self, ui):
        self.xmlfile = ui.xmlfile.text()
        self.tab_space = ui.tab_space.value()
        self.max_line_char_counts = ui.max_line_num.value()
        self.product_id = ui.product_id.text()
        self.output_path = ui.output_path.text()
        self.author = ui.author.text()
        self.filter_struct = ui.filter_struct.toPlainText()
        self.need_remove_item = ui.need_remove_item.text()
        self.include_headers = ui.include_headers.toPlainText()
        self.custom_define_dict = ui.custom_define_dict.toPlainText()
        self.is_const = ui.is_const.isChecked()
        self.add_custom_defines = ui.add_custom_defines.toPlainText()
        self.copyright = ui.copyright.toPlainText()

    def set_params(self, ui):
        ui.xmlfile.setText(self.xmlfile)
        ui.tab_space.setValue(self.tab_space)
        ui.max_line_num.setValue(self.max_line_char_counts)
        ui.product_id.setText(self.product_id)
        ui.output_path.setText(self.output_path)
        ui.author.setText(self.author)
        ui.filter_struct.setPlainText(self.filter_struct)
        ui.need_remove_item.setText(self.need_remove_item)
        ui.include_headers.setPlainText(self.include_headers)
        ui.is_const.setChecked(self.is_const)
        ui.add_custom_defines.setPlainText(self.add_custom_defines)
        ui.copyright.setPlainText(self.copyright)
        ui.custom_define_dict.setPlainText(self.custom_define_dict)


class PQtoolsToCode(SubWindow):
    def __init__(self, name, parent=None):
        super().__init__(name, parent, Ui_PQtoolsToCode())
        self.params = self.load_params(PQtoolsParams())
        self.params.set_params(self.ui)
        self.ui.generate.clicked.connect(self.generate_code)
        self.ui.openxmlfile.clicked.connect(self.set_xmlpath)
        self.ui.open_output_path.clicked.connect(self.set_output_path)

    def set_xmlpath(self):
        xmlpath = QFileDialog.getOpenFileName(
            None, '打开pqtools生成的xml', './', "XML (*.xml)")
        xmlfile = xmlpath[0]
        if (xmlfile != ''):
            self.ui.xmlfile.setText(xmlfile)
            self.params.xmlfile = xmlfile
    
    def set_output_path(self):
        output_path = QFileDialog.getSaveFileName(
                None, '保存为头文件', './', "头文件 (*.h)")
        output_path = output_path[0]
        if (output_path != ''):
            self.ui.output_path.setText(output_path)
            self.params.output_path = output_path

    def generate_code(self):
        self.params.get_params(self.ui)
        filename = self.params.output_path
        filename_nosuffix = filename.split('/')[-1]
        if os.path.exists(filename):
            os.remove(filename)
        head = "#ifndef _" + self.params.product_id.upper() + "_" + filename_nosuffix.upper().replace(".", "_") + \
        "_\n" + "#define _" + self.params.product_id.upper() + "_" + filename_nosuffix.upper().replace(".", "_") + \
        "_\n\n" + self.params.include_headers + '\n'\
            + """
#ifdef __cplusplus
#if __cplusplus
extern "C" {
#endif
#endif
""" + '\n' + self.params.add_custom_defines + '\n\n'
        custom_define_dict_list = self.params.custom_define_dict.split(":")
        custom_define_dict = {
            custom_define_dict_list[0]: custom_define_dict_list[1]
        }

        end = """#ifdef __cplusplus
#if __cplusplus
}
#endif
#endif /* End of #ifdef __cplusplus */

#endif
"""
        xmldata = xmldom.parse(self.params.xmlfile)
        data = xmldata.getElementsByTagName('SAVE_DATA')
        dataStruct = DataStruct(xmldata)

        if(len(self.params.filter_struct) == 0):
            self.params.filter_struct = dataStruct.mlist
        strGen = None

        with open(filename, 'a') as f:
            f.write(head)

        for node in data:
            name = node.getAttribute('PATH').split('.')
            value = node.getAttribute('VALUE')
            if(strGen is not None):
                if(name[0] != strGen.pri_name_0):
                    strGen.finish(self.params.filter_struct)
                    strGen = StructGen(
                        name, dataStruct, self.params, custom_define_dict)
                    strGen.add(name, value)
                else:
                    strGen.add(name, value)
            else:
                strGen = StructGen(
                    name, dataStruct, self.params, custom_define_dict)

        with open(filename, "a") as f:
            f.write(end)
        with open(filename, "r") as f:
            text = f.read()
            self.ui.dst_file.setText(text)


class StructGen:
    def __init__(self, name, dataStruct, params, custom_define_dict):
        self.filename = params.output_filename
        self.is_const = params.is_const
        self.TAB_SPACE = " " * params.tab_space
        self.NEED_REMOVE_ITEM = params.need_remove_item
        self.MAX_CHAR_COUNT_PER_LINE = params.max_line_char_counts
        self.product_id = params.product_id
        self.dataStruct = dataStruct
        self.name = name[0]
        if(self.name in custom_define_dict):
            self.name = custom_define_dict[self.name]
        self.pri_name_0 = name[0]
        self.old_name = []
        self.data = []
        self.level = 0
        self.line = 0
        self.last_index = 0
        self.tmp_data = 0
        self.old_mem_length = 0
        namestr = "".join(map(lambda x: x.capitalize(), self.name.split("_")))
        if self.is_const == True:
            self.data.append(
                "static const struct " + self.name + " g_" + self.product_id.capitalize() + namestr[:-1] + " = {")
        else:
            self.data.append(
                "static struct " + self.name + " g_" + self.product_id.capitalize() + namestr[:-1] + " = {")

    def change_key(self, key):
        """
        修改括号嵌套的层级，如果key大于当前的层级，就加一个'{'括号，如果小于当前层级就加一个'}'
        key: 输入的层级
        """
        while(self.level < key):
            self.data.append(self.TAB_SPACE*self.level + "{")
            self.level += 1
        while(self.level > key):
            self.level -= 1
            # 去除}前面的,
            self.data[-1] = self.data[-1][:-1]
            self.data.append(self.TAB_SPACE*self.level + "},")

    def add(self, name, string, Debug_attr=None):
        """
        增加一个结构体的值
        name: 结构体的名称
        string: 结构体对应的值
        """
        if Debug_attr is None or self.name == Debug_attr:
            # 找到从第几个数开始不同
            for i in range(len(name)):
                if i < len(self.old_name):
                    if(name[i] != self.old_name[i]):
                        key = i
                        break
                else:
                    key = i
                    break

            # 排除数组的影响，如果检测到数组，key需要+1
            for i in range(min(len(self.old_name), len(name))):
                if("[" in name[i]):
                    namesubstr = name[i].split('[')
                    oldnamesubstr = self.old_name[i].split('[')
                    if(namesubstr[0] == oldnamesubstr[0]):
                        key += 1

            self.change_key(key)
            key = len(name) - 1

            # 排除数组的影响，如果检测到数组，key需要+1
            for i in range(len(name)):
                if("[" in name[i]):
                    key += 1
            self.change_key(key)

            # 如果是第一次设置的话，需要去除第一行的'{'
            if(self.line == 0):
                self.data.pop(1)
            self.old_name = name
            self.line += 1
            if(string.find(',') == -1):
                # 一个数
                bit = self.dataStruct.get_member_bit(name)
                # mem_length = self.dataStruct.get_member_len(name)
                # 如果没有bit的属性就直接输出
                if(bit is None or len(bit) == 0):
                    self.data.append(
                        self.TAB_SPACE*self.level + '// ' + name[-1])
                    self.data.append(self.TAB_SPACE*self.level + string + ',')
                else:
                    if(name[-1] != self.NEED_REMOVE_ITEM):
                        self.data.append(
                            self.TAB_SPACE*self.level + '// ' + name[-1])
                        self.data.append(
                            self.TAB_SPACE*self.level + "." + name[-1] + " = " + string + ',')

                # self.old_mem_length = mem_length
            else:
                member_size = self.dataStruct.get_member_count(name)
                if(member_size is not None):
                    (row, col) = member_size
                    self.data.append(
                        self.TAB_SPACE*self.level + '// ' + name[-1])
                    if(row == 1):
                        # cleancode: ,后面加空格
                        num = string.split(',')
                        string = ", ".join(num)
                        self.long_str_append(string, self.level)
                    else:
                        num = string.split(',')
                        self.data.append(self.TAB_SPACE*self.level + "{")
                        for i in range(row):
                            tmpstr = ", ".join(num[i*col:(i+1)*col])
                            self.long_str_append(tmpstr, self.level+1)
                        self.data.append(self.TAB_SPACE*self.level + "},")
                else:
                    self.data.append(
                        self.TAB_SPACE*self.level + '// ' + name[-1])
                    # cleancode: ,后面加空格
                    num = string.split(',')
                    string = ", ".join(num)
                    self.long_str_append(string, self.level)

    def long_str_append(self, string, level):
        """
        根据一行最大字符数MAX_CHAR_COUNT_PER_LINE，对长字符串进行拆分
        为了符合cleancode规范
        string: 输入的字符串
        level: 当前的层级
        """
        long_str = self.TAB_SPACE*level + "{" + string + "}" + ','
        length = len(long_str)
        while(length > 0):
            if(length > self.MAX_CHAR_COUNT_PER_LINE):
                clip_str = long_str[0:self.MAX_CHAR_COUNT_PER_LINE]
                clip_str_index = clip_str.rfind(',')
                clip_str = clip_str[0:clip_str_index+1]
                self.data.append(clip_str)
                long_str = self.TAB_SPACE*level + long_str[clip_str_index+1:]
                length -= len(clip_str)
            else:
                self.data.append(long_str)
                length = 0

    def finish(self, filter_struct=None):
        """
        该结构体结束，对该结构体进行打印
        filter_struct: 对打印进行过滤，只会打印该列表里面有的结构体
        """
        self.change_key(0)
        self.data[-1] = '};'
        if self.name in filter_struct:
            with open(self.filename, "a") as f:
                for data in self.data:
                    f.write(data + '\n')
                f.write("\n")


class DataStruct:
    def __init__(self, xmldata):
        self.member = xmldata.getElementsByTagName('STRUCT')
        self.dict = {}
        self.mlist = []
        for i, member in enumerate(self.member):
            self.dict[member.getAttribute('ID')] = i
            self.mlist.append(member.getAttribute('ID'))

    def get_member_count(self, name):
        """
        获取当前结构体的size，是一维数组还是多维数组，每行每列的长度
        name: 输入结构体的名字
        """
        typeName = name[0]
        if(name[0] in self.dict):
            for i in range(len(name)-1):
                submens = self.member[self.dict[typeName]
                                      ].getElementsByTagName('MEMBER')
                for submen in submens:
                    if(submen.getAttribute('ID') == name[i+1].split('[')[0]):
                        if(i >= len(name) - 2):
                            count_list = submen.getAttribute(
                                'TITLE').split(';')
                            if(len(count_list) > 1):
                                row = count_list[0].split('(')[0]
                                col = count_list[1].split('(')[0]
                                if(row.isdigit() and col.isdigit()):
                                    return (int(row), int(col))
                                else:
                                    return (1, -1)
                            else:
                                return (1, -1)
                        else:
                            typeName = submen.getAttribute('TYPE')
        return None

    def get_member_len(self, name):
        """
        获取当前结构体的字节长度
        name: 输入结构体的名字
        """
        typeName = name[0]
        if(name[0] in self.dict):
            for i in range(len(name)-1):
                submens = self.member[self.dict[typeName]
                                      ].getElementsByTagName('MEMBER')
                for submen in submens:
                    if(submen.getAttribute('ID') == name[i+1].split('[')[0]):
                        typeName = submen.getAttribute('TYPE')
        if typeName == "HI_U16":
            return 16
        elif typeName == "HI_U8":
            return 8
        elif typeName == "HI_U32":
            return 32
        elif typeName == "HI_U64":
            return 64
        else:
            return 0

    def get_member_bit(self, name):
        """
        获取当前结构体的bit
        name: 输入结构体的名字
        """
        typeName = name[0]
        if(name[0] in self.dict):
            for i in range(len(name)-1):
                submens = self.member[self.dict[typeName]
                                      ].getElementsByTagName('MEMBER')
                for submen in submens:
                    if(submen.getAttribute('ID') == name[i+1].split('[')[0]):
                        if(i >= len(name) - 2):
                            return submen.getAttribute('BITS')
                        else:
                            typeName = submen.getAttribute('TYPE')
        return None
