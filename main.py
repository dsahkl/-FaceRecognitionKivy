from kivy.uix.listview import ListItemButton
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
import load_data
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
import cv2
import os
from kivy.uix.popup import Popup
import pickle
import face_recognition
import collections





def directory_args_converter(index, data_item):
    return {'directory_pos': data_item}

def image_args_converter(index, data_item):
    name, id, path, _ = data_item

    return {'del_peo_information': (name, id, path)}

class PopDelete(Popup):
    pass


class AddDataMethod(Popup):
    pass

class AddMembersFromFile(BoxLayout):
    pass

class LocationButton(ListItemButton):
    del_peo_information = ObjectProperty()


class FaceRoot(BoxLayout):



    # 指向文档的text_input
    text_input = ObjectProperty()

    # popup choose from file
    choose_file_popup = ObjectProperty()

    # id 指向delete_members widget
    delete_members = ObjectProperty()
    # 两个popup界面
    pop_delete = ObjectProperty()
    add_data_choices = ObjectProperty()
    # 存储要删除成员照片和名字
    del_members_inform = ObjectProperty()

    # 主界面
    carousel = ObjectProperty()
    capture = None
    text_input_camera = ObjectProperty()
    image = ObjectProperty()
    # popup
    warning = ObjectProperty()
    # picture form
    recognition_interface = ObjectProperty()
    def __init__(self, **kwargs):
        # 在这创建三个私有变量来存储识别后的数据，好像应该不需要显示工号，
        # 但还是保留一下吧
        self.__name =[]
        self.__ID = []
        self.__embedding =[]
        # 一个私有变量来存储数据
        self.__image_data= []
        super().__init__(**kwargs)
        # 首先将数据加载到内存中
        self.__store_data = JsonStore("image_data.json")
        # 两个只要有一个不存在就要重新加载好一点吧，这个地方反正是自己定义的
        if self.__store_data.exists('image_data'):
            # 从文件夹中将数据加载到内存中
            self.__image_data = self.__store_data.get('image_data')['image_data']

            # 加载self.emb 仍然是从内存中加载

        else:
            # 转到add_members界面
            Clock.schedule_once(lambda dt: self.show_load_data_choices())
    def camera_load_data_start(self):
        # global capture  弱检查
        if '+' not in self.add_members_camera.text_input_camera.text:
            # 添加一个popup
            # self.add_widget(Popup(title='Warning', content=Label(text='Please Enter The Name')))
            self.warning = Warning()
            self.warning.open()
        else:
            self.capture = cv2.VideoCapture(0)
            self.capture.set(3, 320)
            self.capture.set(4, 240)
            self.add_members_camera.camera_load.start(self.capture)
    # 这个地方明天需要修改 2018.9.3
    def camera_recognition_start(self):
        # 在这个地方数据提取
        self.__name, self.__ID, _, self.__embedding = zip(*self.__image_data)
        self.capture = cv2.VideoCapture(0)
        self.capture.set(3, 640)
        self.capture.set(4, 480)




        self.recognition_interface.camera_recognition.start(self.capture, self.__name, self.__ID, self.__embedding)

    def doexit(self):
        # global capture
        if self.capture != None:
            self.capture.release()
            # print('release cv')
            self.capture = None
        # EventLoop.close()

    def load_data_camera(self, name):
        # 获取text内容  for example: duanshengshun+0006+1
        name_, id, _ = name.split('+')
        output_relative_path = '+'.join((name_, id))
        input_real_path = './cache'
        path = (input_real_path, output_relative_path)

        # 将数据加载到内存中
        dataset= load_data.load_image_data(path)
        self._load_image(dataset)

        # 删除文件并重置为默认图片
        delete_path = './cache/{}.jpg'.format(name)
        os.remove(delete_path)
        self.add_members_camera.image.source = ''

        # 加载成功之后转换方式
    def _load_image(self, dataset):
        if len(self.__image_data) != 0:
            # 添加数据了
            self.__image_data.extend(dataset)
        else:
            self.__image_data = dataset
        # 将新数据添加到内存中
        store = JsonStore("image_data.json")
        store.put("image_data",
                  image_data=self.__image_data
                  )

    def load_data_from_file(self, path):
        # print(path)
        dataset =load_data.load_image_to_directory_data(path)
        # data, _ = load_data.load_image_and_address('./data')
        # self.image_path = data
        self._load_image(dataset)

        # print(self.image_path)


    def Name_search_results(self):
        text = self.delete_members.search_input.text
        self.delete_members.search_results_list.adapter.data.clear()
        for person in self.__image_data:
            # 修改一下，匹配模糊搜索,
            if text.lower() in person[0].lower() :

                self.delete_members.search_results_list.adapter.data.append(person)

    def ID_search_results(self):
        text = self.delete_members.search_input.text
        self.delete_members.search_results_list.adapter.data.clear()
        for person in self.__image_data:
            # 修改一下，匹配模糊搜索,
            if text.lower() == person[1].lower():
                self.delete_members.search_results_list.adapter.data.append(person)

    def show_pop_inform(self, del_peo_information):
        self.del_members_inform = del_peo_information
        self.pop_delete = PopDelete()
        self.pop_delete.open()

    def pop_person_from_database(self, information):

        '''
        从'./data'中删除
        从__image_data中删除
        :param information:
        :return:
        '''
        # 重新赋值为0
        load_data.person_number_dictionary_used_ID[information[1]] = 0
        remove_item = []
        for item in self.__image_data:
            # ID是唯一标识，这里只判断ID就可以了
            # print(information[1],item[1], information[1] == item[1], item[2])
            if information[1] == item[1]:
                remove_item.append(item)
        for item in remove_item:
            self.__image_data.remove(item)
            self.delete_members.search_results_list.adapter.data.remove(item)
        # 添加测试代码 删除后打印名字和id
        # for item in self.__image_data:
        #     print('name {}, path{}'.format(item[0], item[2]))
        self.delete_members.search_results_list._trigger_reset_populate()
        self.__store_data.put("image_data",
                               image_data=self.__image_data
                             )
        dir = '{}+{}'.format(information[0], information[1])
        load_data.delete_person(dir)
        self.pop_delete.dismiss()
    def show_load_data_choices(self):
        self.add_data_choices = AddDataMethod()
        self.add_data_choices.open()


    def get_win_drives(self):

        if platform == 'win':
            # 平台化处理
            import win32api

            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]

            return drives
        else:
            # 这个地方将来要填linux系统的
            return []

    def show_choose_file_popup(self):
        self.choose_file_popup = ChooseFilePopup()
        self.choose_file_popup.drives_list.adapter.data.extend(self.get_win_drives())
        self.choose_file_popup.open()

    def drive_selection_changed(self, pos):
        # print(pos)
        self.choose_file_popup.file_chooser.path = pos

    def load_file(self, path, file_name):
        # print(file_name)
        self.add_members_file.text_input.text = file_name[0]


class DeleteMembers(BoxLayout):
    del_peo_information = ObjectProperty()
class AddMembersFromCamera(BoxLayout):
    pass

class FaceApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_stop(self):
        with open('./person_number_dictionary_used_ID.pickle', 'wb') as f:
            pickle.dump(load_data.person_number_dictionary_used_ID, f)
        super().on_stop()


class ChooseFilePopup(Popup):
    pass


class DirectoryButton(ListItemButton):
    directory_pos = ObjectProperty()

class CameraLoadData(Image):


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capture = None

    def start(self, capture, fps=30):
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def stop(self):
        Clock.unschedule_interval(self.update)
        self.capture = None

    def update(self, dt):
        return_value, frame = self.capture.read()
        if return_value:
            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(w, h))
                texture.flip_vertical()
            texture.blit_buffer(frame.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()


class CameraFaceRecognition(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__capture = None
        self.__name = None
        self.__ID = None
        self.__embedding = None

    def start(self, capture, name, id, embedding,fps=10):
        self.__capture = capture
        self.__name = name
        self.__ID = id
        self.__embedding = embedding
        Clock.schedule_interval(self.update_face_racognition, 1.0 / fps)


    def stop(self):
        Clock.unschedule_interval(self.update_face_racognition)

    def update_face_racognition(self, dt):
        return_value, frame = self.__capture.read()

        rgb_frame = frame[:, :, ::-1]
        if return_value:

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            # 继续修改 2018 09 03  将数据提取出来使用的
            names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(self.__embedding, face_encoding)
                name = 'Unknown'
                if True in matches:
                    matchedIdex = [i for (i, b) in enumerate(matches) if b]
                    counts = collections.defaultdict(int)
                    # 这个地方到后边是还需要修改的呢
                    for i in matchedIdex:
                        name = self.__name[i]
                        id = self.__ID[i]
                        name_id = '{}({})'.format(name, id)
                        counts[name_id] += 1

                    name = max(counts, key=counts.get)
                names.append(name)
            for ((top, right, bottom, left), name) in zip(face_locations, names):
            #     cv2.rectangle(rgb_frame, (left, top), (right, bottom), (0, 0, 255), 2)
            #     y = top - 15 if top - 15 > 15 else top + 15
            #     cv2.putText(rgb_frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
            #                 0.75, (0, 255, 0), 2)
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        texture = self.texture
        w, h = rgb_frame.shape[1], rgb_frame.shape[0]
        if not texture or texture.width != w or texture.height != h:
            self.texture = texture = Texture.create(size=(w, h))
            texture.flip_vertical()
        texture.blit_buffer(rgb_frame.tobytes(), colorfmt='rgb')
        self.canvas.ask_update()





class Warning(Popup):
    pass
if __name__ == '__main__':
    FaceApp().run()
