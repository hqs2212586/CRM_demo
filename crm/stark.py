# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'

from stark.service.stark import site, ModelStark

from .models import *
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse, redirect, render

site.register(School)


class UserConfig(ModelStark):
    list_display = ["name", "email", "depart"]


site.register(UserInfo, UserConfig)


class ClassConfig(ModelStark):
    def display_classname(self, obj=None, header=False):
        # 班级名
        if header:
            return "班级名称"
        # 将课程名和班级期数合并为班级名
        # obj.course是课程对象  obj.course.name是课程名称  obj.semester是数字需要转字符串
        class_name = "%s(%s)" % (obj.course.name, str(obj.semester))
        return class_name

    list_display = [display_classname, "tutor", "teachers"]


site.register(ClassList, ClassConfig)

from django.http import JsonResponse

class StudentConfig(ModelStark):
    def score_view(self, request, sid):   # sid:当前学生的id
        """扩展视图"""
        if request.is_ajax():
            # 处理ajax请求
            print(request.GET)
            sid = request.GET.get("sid")
            cid = request.GET.get("cid")
            # 去studyrecord查看学生对应课程所有学习记录  课程需要跨表查询
            study_record_list = StudyRecord.objects.filter(student=sid, course_record__class_obj=cid)

            data_list = []
            for study_record in study_record_list:
                day_num = study_record.course_record.day_num
                data_list.append(["day%s" % day_num, study_record.score])    # 和highchart的data要求格式相同列表包列表
            print(data_list)   # [['day1', -1], ['day95', 80]]
            return JsonResponse(data_list, safe=False)  # 序列化不是一个字典必须改为False
        else:

            student = Student.objects.filter(pk=sid).first()
            class_list = student.class_list.all()     # 班级列表
            return render(request, "score_view.html", locals())

    def extra_url(self):
        """扩展路由"""
        temp = []
        temp.append(url((r"score_view/(\d+)"), self.score_view))
        return temp

    def score_show(self, obj=None, header=False):
        """查看成绩"""
        if header:
            return "查看成绩"
        return mark_safe("<a href='/stark/crm/student/score_view/%s'>查看成绩</a>" % obj.pk)

    list_display = ['customer', 'class_list', score_show]
    list_display_links = ['customer']


site.register(Student, StudentConfig)

from django.conf.urls import url


class CustomerConfig(ModelStark):
    # 如果要展示性别
    def display_gender(self, obj=None, header=False):
        if header:
            return "性别"
        return obj.get_gender_display()

    def display_course(self, obj=None, header=False):   # obj:客户对象
        """咨询的课程"""
        if header:
            return "课程"
        temp = []
        for course in obj.course.all():   # 遍历所有的课程
            s = "<a href='/stark/crm/customer/cancel_course/%s/%s' " \
                "style='border:1px solid #369;padding:3px 6px;'>" \
                "<span>%s</span></a>&nbsp;" % (obj.pk, course.pk, course.name)
            temp.append(s)
        return mark_safe("".join(temp))

    def cancel_course(self, request, customer_id, course_id):
        print(customer_id, course_id)

        obj = Customer.objects.filter(pk=customer_id).first()
        obj.course.remove(course_id)   # 删除对象所有的关联课程
        return redirect(self.get_list_url())   # 重定向当前表的查看页面

    def public_customer(self, request):
        """公共客户"""
        # 未报名、且三天未跟进或15天未成单
        from django.db.models import Q
        import datetime
        now = datetime.datetime.now()   # datetime.datetime：表示日期时间
        # datetime.timedelta：表示时间间隔，即两个时间点之间的长度
        delta_day3 = datetime.timedelta(days=3)
        delta_day15 = datetime.timedelta(days=15)

        # 三天未跟进:now-last_consult_date>3  ===> last_consult_date < now - 3
        # 15天未成单:now-recv_data > 15  ====> recv_data < now - 15
        user_id = 2  # 课程顾问吴三江
        customer_list = Customer.objects.filter(Q(last_consult_date__lt=now - delta_day3) | Q(recv_date__lt=now - delta_day15), status=2).exclude(consultant_id=user_id)
        print(customer_list)   # <QuerySet [<Customer: 小东北>, <Customer: 泰哥>]>
        return render(request, "public.html", locals())

    def further(self, request, customer_id):
        """跟进客户"""
        user_id = 2  # 这里是模拟登陆状态requet.session.get("user_id")
        import datetime
        from django.db.models import Q
        now = datetime.datetime.now()
        delta_day3 = datetime.timedelta(days=3)
        delta_day15 = datetime.timedelta(days=15)
        # 为符合条件客户更改课程顾问，避免多人同时或连续跟进
        ret = Customer.objects.filter(pk=customer_id).filter(Q(last_consult_date__lt=now - delta_day3) | Q(recv_date__lt=now - delta_day15), status=2).update(consultant=user_id, last_consult_date=now, recv_date=now)
        if not ret:
            # 没有更新
            return HttpResponse("已经被跟进了")

        # 添加一条记录  状态均是正在跟进状态
        CustomerDistrbute.objects.create(customer_id=customer_id, consultant_id=user_id, date=now, status=1)

        return HttpResponse("跟进成功！")

    def mycustomer(self, request):
        """我的客户"""
        user_id = 2
        customer_distribute_list = CustomerDistrbute.objects.filter(consultant=user_id)

        return render(request, "mycustomer.html", locals())

    def extra_url(self):
        """扩展路由"""
        temp = []
        temp.append(url((r"cancel_course/(\d+)/(\d+)"), self.cancel_course))
        temp.append(url(r"public/", self.public_customer))
        temp.append(url(r"further/(\d+)", self.further))
        temp.append(url(r"mycustomer/", self.mycustomer))
        return temp

    list_display = ["name", display_gender, display_course, "consultant"]


site.register(Customer, CustomerConfig)


class DepartmentConfig(ModelStark):
    list_display = ['title', 'code']


site.register(Department, DepartmentConfig)
site.register(Course)


class ConsultRecordConfig(ModelStark):
    list_display = ["customer", "consultant", "date", "note"]  # note是跟进记录


site.register(ConsultRecord, ConsultRecordConfig)


class CourseRecordConfig(ModelStark):
    def score(self, request, course_record_id):
        if request.method == "POST":
            # print(request.POST)
            # <QueryDict: {'csrfmiddlewaretoken': ['20Zp72PlKJzRZ6HAYkMX0veCIxynx5nogd8LsKKkdZb7mRLrAb1KtN1PDTljh7Jq'], 'score_4': ['70'], 'homework_note_4': ['学习理解能力差'], 'score_5': ['40'], 'homework_note_5': ['无纪律无组织'], 'score_6': ['90'], 'homework_note_6': ['学习能力优秀']}>
            data = {}
            for key, value in request.POST.items():   # 键、值
                if key == "csrfmiddlewaretoken":
                    continue
                # 分隔score_1为例，score为字段  1为某一个学生学习记录的pk值
                field, pk = key.rsplit("_", 1)  # 从右开始以"_"分隔数据,且仅分隔一次   字段、主键

                # dic = {1:{"homework_note":"", "score":90}, 2:{"homework_note": "", "score": 76}}
                if pk in data:
                    # 第一次加入字典
                    data[pk][field] = value
                else:
                    # pk已经保存在字典中
                    data[pk] = {field: value}

            print("data", data)  # data {'4': {'score': '100', 'homework_note': 'dsfe '}, '5': {'score': '85', 'homework_note': 'asd a'}, '6': {'score': '50', 'homework_note': 'adad w'}}

            for pk, update_data in data.items():   # 主键、更新数据
                StudyRecord.objects.filter(pk=pk).update(**update_data)

            return redirect(request.path)  # 拿到当前POST请求路径重定向GET请求
        else:
            study_record_list = StudyRecord.objects.filter(course_record=course_record_id)   # 过滤出对应课程（哪个班级哪一天）的学习记录

            score_choices = StudyRecord.score_choices
            return render(request, "score.html", locals())

    def extra_url(self):
        """扩展考勤记录url"""
        temp = []
        temp.append(url(r"record_score/(\d+)", self.score))
        return temp

    # 定制一栏新的表格
    def record(self, obj=None, header=False):
        if header:
            return "考勤"
        return mark_safe("<a href='/stark/crm/studyrecord/?course_record=%s'>记录</a>" % obj.pk)    # mark_safe取消转义

    def record_score(self, obj=None, header=False):
        if header:
            return "录入成绩"
        # http://127.0.0.1:8000/stark/crm/studyrecord/?course_record=1  CourseRecord主键值
        return mark_safe("<a href='record_score/%s'>录入成绩</a>" % obj.pk)

    list_display = ["class_obj", "day_num", "teacher", record, record_score]

    def patch_studyRecord(self, request, queryset):
        print("=====>",queryset)
        """
        提交批量操作获取的queryset
        <QuerySet [<CourseRecord: python基础(9期) day94>, <CourseRecord: python基础(9期) day95>]>
        """
        temp = []
        for course_record in queryset:
            # 过滤course_record关联的班级对应的所有的学生  学生表classlist关联班级表
            student_list = Student.objects.filter(class_list__id=course_record.class_obj.pk)   # 学生的班级id和课程记录班级的id进行比对  拿到班级所有的学生
            for student in student_list:   # 拿到学生对象
                obj = StudyRecord(student=student, course_record=course_record)
                temp.append(obj)

        StudyRecord.objects.bulk_create(temp)   # 批量插入

    actions = [patch_studyRecord, ]
    patch_studyRecord.short_description = "批量生产学习记录"
    """
    def get_action_list(self):
        # 获取自定义批量操作
        temp = []
        for action in self.actions:
            temp.append({
                "name": action.__name__,    # 函数.__name__：拿到函数名
                "desc": action.short_description
            })  # [{"name": "patch_init", "desc": "批量处理"}]
        return temp
    """


site.register(CourseRecord, CourseRecordConfig)


class StudyConfig(ModelStark):
    list_display = ["student", "course_record", "record", "score"]

    def patch_late(self, request, queryset):
        queryset.update(record="late")

    patch_late.short_description = "迟到"
    actions = [patch_late, ]


site.register(StudyRecord, StudyConfig)