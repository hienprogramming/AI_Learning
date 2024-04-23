
'''
    Đọc 1 component để in ra số lượng file .py trong thư mục và CIT_CMD_0010, CIT_CMD_0020, CIT_CMD_0030
'''
import os
import re

# Đường dẫn đến thư mục chứa các file .py
folder_path = r'D:\AI\LearingAI\Excel\Test_CMD'

file_list = os.listdir(folder_path)
py_files = [file for file in file_list if file.endswith('.py')]
num_py_files = len(py_files)

def extract_test_case_name(file_names):
    test_case_names = []
    for file_name in file_names:
        match = re.match(r'Test_CMD_(\w+)\.py', file_name)
        if match:
            test_case_names.append(match.group(1))
    return test_case_names

# Mở file excel.txt để ghi kết quả
with open(os.path.join(folder_path, 'excel.txt'), 'w', encoding="utf-8") as file:
    file.write(f"Số lượng file python trong thư mục: {num_py_files}\n")
    # Duyệt qua các file trong thư mục
    for filename in os.listdir(folder_path):
        # Kiểm tra nếu là file .py và có tên phù hợp
        # if filename.endswith('.py') and re.match(r'CIT_CMD_00[1-3]0\.py', filename):
        if filename.endswith('.py'):
            test_case_names = extract_test_case_name([filename])
            file.write(", ".join(test_case_names) + '\n')







'''
    Xử lí excel file
'''

# import pandas as pd

# # Đọc nội dung từ file Sahara.xlsx
# sahara_df = pd.read_excel('D:\\AI\\LearingAI\\Excel\\Sahara.xlsx', sheet_name='TestCase')

# # Đọc nội dung từ file regression.xlsx
# regression_df = pd.read_excel('D:\\AI\\LearingAI\\Excel\\regression.xlsx', sheet_name='Regression')

# # Tìm và so sánh CIT_CMD_0010, CIT_CMD_0020, CIT_CMD_0030
# for index, row in sahara_df.iterrows():
#     CIT_CMD_0010 = row['Link']
#     CIT_CMD_0020 = row['Link']
#     CIT_CMD_0030 = row['Link']
#     for index2, row2 in regression_df.iterrows():
#         if (row2['Testacace'] == CIT_CMD_0010 or 
#             row2['Testacace'] == CIT_CMD_0020 or 
#             row2['Testacace'] == CIT_CMD_0030):
#             regression_df.at[index2, 'ASIL'] = row['Safety']

# # Lưu lại file regression.xlsx với cột ASIL đã được cập nhật
# regression_df.to_excel('D:\\AI\\LearingAI\\Excel\\regression.xlsx', index=False)


# import pandas as pd

# # Đọc nội dung từ file Sahara.xlsx
# sahara_df = pd.read_excel('D:\\AI\\LearingAI\\Excel\\Sahara.xlsx', sheet_name='TestCase')

# # Đọc nội dung từ file regression.xlsx
# regression_df = pd.read_excel('D:\\AI\\LearingAI\\Excel\\regression.xlsx', sheet_name='Regression')

# # Tìm và so sánh CIT_CMD_0010, CIT_CMD_0020, CIT_CMD_0030
# for index, row in sahara_df.iterrows():
#     CIT_CMD_0010 = row['Link']
#     CIT_CMD_0020 = row['Link']
#     CIT_CMD_0030 = row['Link']
#     for index2, row2 in regression_df.iterrows():
#         if (row2['Testacace'] == CIT_CMD_0010 or 
#             row2['Testacace'] == CIT_CMD_0020 or 
#             row2['Testacace'] == CIT_CMD_0030):
#             regression_df.at[index2, 'ASIL'] = row['Safety']

# # Lưu lại file regression.xlsx với cột ASIL đã được cập nhật
# regression_df.to_excel('D:\\AI\\LearingAI\\Excel\\regression.xlsx', index=False)


# # Đọc nội dung từ file excel.txt
# with open('excel.txt', 'r', encoding="utf-8") as file:
#     content = file.readlines()

# # Xác định số lượng file python từ dòng đầu tiên
# num_files = int(content[0].split()[-1])

# # Tạo danh sách các CIT_CMD từ nội dung còn lại của file
# cit_commands = [line.strip() for line in content[1:]]

# # Tạo mapping giữa CIT_CMD và các tên file python
# cit_mapping = {f'CIT_CMD_{i+1:04d}': cit_commands[i] for i in range(num_files)}

# # Sử dụng mapping để thay thế các giá trị trong đoạn mã
# for cit_cmd, file_name in cit_mapping.items():
#     # Thực hiện thay thế trong đoạn mã của bạn
#     # Ví dụ:
#     # code = code.replace(f"{cit_cmd} = row['Link']", f"{cit_cmd} = '{file_name}'")
#     replacement = f"{cit_cmd} = '{file_name}'"
#     print(replacement)
