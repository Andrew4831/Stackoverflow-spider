import os

def delete_files_in_directory(directory_path):
    try:
        # 获取目录下的所有文件列表
        file_list = os.listdir(directory_path)

        for filename in file_list:
            file_path = os.path.join(directory_path, filename)

            # 如果文件是普通文件，则删除
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

        print("All files in the directory have been deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # 指定目录路径
    answer_path = "output/answer"
    comment_path = "output/comment"
    question_path = "output/question"
    user_path = "output/user"
    # with open('output/answer/a.json','w') as f:
    #     f.write('s')

    # 调用函数删除目录下的所有文件
    delete_files_in_directory(answer_path)
    delete_files_in_directory(comment_path)
    delete_files_in_directory(question_path)
    delete_files_in_directory(user_path)
