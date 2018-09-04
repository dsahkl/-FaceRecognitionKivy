import os
import cv2
import shutil  # 删除非空文件夹
# 改一下，使用内置的试一试
import face_recognition
from scipy import misc
import matplotlib.pyplot as plt
from kivy.storage.jsonstore import JsonStore
from scipy import misc
import collections
import pickle
# 默认为0啊 全局维护数量的 这个鬼玩意也得保存到内存中。。。先去个厕所。！
# 用pickle吧
with open('./person_number_dictionary_used_ID.pickle', 'rb') as f:
    person_number_dictionary_used_ID = pickle.load( f)

# def get_image_paths(facedir):
#     # err_code = 1
#     if os.path.isdir(facedir):
#         images = os.listdir(facedir)
#         try:
#             if len(images) == 0:
#                 err = '文件夹"{}"下无照片'.format(facedir)
#                 raise(Exception(err))
#             elif len(images) != 1:
#                 err = '文件夹"{}"下照片数量为{}张，不合法'.format(facedir, len(images))
#                 raise (Exception(err))
#
#             image_path = os.path.join(facedir, images[0])
#         except Exception as err:
#             print(err)
#
#     return image_path

# 修改这个函数 2018.09.03   2018.09.04 将此函数作为调用的子函数
def load_image_data(file_path):
    '''    这次就往里加照片就好了，先不用限制照片数量
    :param file_path: tuple  input_real_path, output_relative_path
    :return:
    '''
    dataset = []
    output_dir = './data'

    output_person_dir = os.path.join(output_dir, file_path[1])
    # print(output_person_dir)

    if not os.path.exists(output_person_dir):
        os.makedirs(output_person_dir)

    name_image = [(entry.split('.')[0], os.path.join(file_path[0], entry))
                  for entry in os.listdir(file_path[0])]
    # print(name_image)
    for name, path in name_image:
            #print(os.path.join(output_path, relative_path))
            image_data = cv2.imread(path)

            # print('save successfully')
            # 注意这个地方，有可能会出bug
            # print(len(name.split('+')))
            name_person, id, _ = name.split('+')
            person_number_dictionary_used_ID[id] += 1
            # print('name: {} number:{}'.format(name_person, person_number_dictionary_used_ID[id]))
            # 重新修改存储格式，
            relative_path = '+'.join((name_person, str(id), str(person_number_dictionary_used_ID[id]))) + '.jpg'
            output_filename = os.path.join(output_person_dir, relative_path)
            # print(output_filename)
            cv2.imwrite(output_filename, image_data)




            # convert bgr to rgb
            image_data = image_data[:, :, ::-1]
            face_encoding = list(face_recognition.face_encodings(image_data)[0])
            # 将数据返回
            #print(name_person, id, output_filename, len(face_encoding))
            dataset.append((name_person, id, output_filename, face_encoding))
    return dataset

def load_image_to_directory_data(filepath):
    data_image = []
    # 传入两个参数， 一个是绝对路径，一个是相对路径
    person_directory = [(os.path.join(filepath, entry), entry) for entry in os.listdir(filepath)]

    for person_path in person_directory:
        print(person_path)
        data_image.extend(load_image_data(person_path))
    return data_image

def delete_person(dir):
    directory = './data'
    shutil.rmtree(os.path.join(directory, dir))

    #print(dataset)

def calculate_embedding(image_data):
    face_emb = []
    for name, im in image_data:
        # 返回的是列表，需要处理一下，这个地方容易出bug
        face_encoding = face_recognition.face_encodings(im)[0]
        # print("name: {0}, emb: {1}".format(name, len(face_encoding)))
        face_emb.append((name, face_encoding))
    return face_emb

if __name__ == '__main__':
    # file = 'F:/Vacation_work/image'
    # load_image_to_directory_data(file)
    # data, _ =load_image_and_address(input_dir)
    # store = JsonStore("image_address.json")
    # store.put("image_path",
    #
    #     image_path=data
    # )
    pass
