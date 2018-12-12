#encoding:utf-8
#导入包
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from encode import Encode

app = Flask(__name__)

#数据库配置信息                                               用户名        密码                数据库名
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:Wang981122.@127.0.0.1/userinfo?charset=utf8'

db = SQLAlchemy(app)

#注册时用的的用户信息表
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=True)
    #加密后的密码32位
    password = db.Column(db.String(50), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer)
    city = db.Column(db.String(20))
    job = db.Column(db.String(50))
    other = db.Column(db.String(200))

#存放在线人员信息的表
class Online(db.Model):
    __tablename__ = 'online'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=True)
    time=db.Column(db.DateTime,nullable=True)

#创建表
db.create_all()

#主界面
@app.route('/')
def main():
    return render_template("index.html")


#登录
@app.route('/login/',methods=["POST","GET"])
def login():
    #Tip提示信息
    Tip = ""
    if( request.method=="POST" ):
        userid = request.form.get("userid")
        password = request.form.get("password")
        if(userid == ""):
            return render_template("register.html")
        U=User.query.filter(User.telephone == userid).first()#根据用户账号查询用户是否存在
        if(U):
            if (Encode(password) == U.password):
                # 如何存在就创建在线用户对象,用来存放在线用户信息
                on_user = Online()#创建
                on_user.username=U.username#用户名
                on_user.time=datetime.now()#登陆时间
                db.session.add(on_user)#插入到数据库
                db.session.commit()#执行
                on_users = Online.query.filter().all()#查询所有在线用户信息
                number = len(on_users)#记录人数
                return render_template("welcome.html",username=U.username,number=number-1)#传参，跳转页面
            else:
                Tip = "账号或密码错误！"#邮箱格式错误
        else:
            Tip = "该账号不存在，请先注册！"#账号不存在
    return render_template("login.html", Tip=Tip)#传参，跳转页面


#注册
@app.route('/register/',methods=["POST","GET"])
def register():
    # Tip提示信息
    Tip = ""
    if(request.method=="POST"):
        username = request.form.get("username")
        telephone = request.form.get("telephone")
        # 根据用户名查询用户是否存在
        U_username = User.query.filter(User.username == username).first()
        # 根据电话号码查询用户是否存在
        U_telephone = User.query.filter(User.telephone == telephone).first()
        if (U_username):
            '''用户名已被注册'''
            Tip = "该用户名已被注册！"
            #注册失败，返回注册界面
            return render_template("register.html", Tip=Tip)
        if(U_telephone):
            '''账号已被注册'''
            Tip = "该电话号码已被注册！"
        else:
            '''账号未被注册'''
            # 创建新用户对象
            user1 = User()
            user1.username = request.form.get("username")

            #密码加密
            password=request.form.get("password")
            user1.password = Encode(password)
            #user1.password = password

            # 验证电话号码格式是否正确
            user1.telephone = request.form.get("telephone")
            if (re.match('^1[0-9]{10}$', user1.telephone)):
                {

                }
            else:
                '''电话格式不合法'''
                Tip = "该电话格式不合法！"
                #电话号码不通过，返回注册界面
                return render_template("register.html", Tip=Tip)

            #验证邮箱格式是否正确
            user1.email = request.form.get("email")
            if(re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.com$',user1.email)):
                user1.gender = request.form.get("gender")
                user1.age = request.form.get("age")
                user1.city = request.form.get("city")
                user1.job = request.form.get("job")
                user1.other = request.form.get("other")

                # 插入数据库
                db.session.add(user1)
                # 执行
                db.session.commit()
                # 注册成功后跳转至登录界面
                return render_template("login.html")
            else:
                '''邮箱格式不合法'''
                Tip = "该邮箱格式不合法！"
    # GET请求或注册不成功都将返回注册界面
    return render_template("register.html", Tip=Tip)


#获取在线用户的基本信息
@app.route('/other_users/',methods=["POST","GET"])
def other_users():
    # 获取url里面传递的用户参数，查询除当前用户外的所有用户信息
    c_u = request.args.get("u")
    if c_u:
        '''如果得到用户名参数u，表明有用户登录，允许查看其他在线用户信息'''
        # 记录[用户信息、用户登录时间、用户id]的列表
        U = []
        # 获取查询框里面的查询内容
        restrict = request.form.get("restrict")
        if restrict:
            '''如果没有获取到内容--》查询所有'''
            #查询所有在线用户
            on = Online.query.filter(Online.username.contains(restrict)).all()
            if on:
                for i in on:
                    # 根据在线用户的用户名去用户信息表里获取对应的用户信息
                    u = User.query.filter(User.username == i.username).first()
                    if u:
                        # 添加记录
                        U.append([u, i.time, i.id])
        else:
            '''如果有获取到内容--》查询满足给定条件的用户'''
            # 查询所有在线用户
            on = Online.query.filter(Online.username!=c_u).all()
            for i in on:
                # 根据在线用户的用户名去用户信息表里获取对应的用户信息
                u = User.query.filter(User.username == i.username).first()
                if u:
                    # 添加记录
                    U.append([u, i.time])
        # 传参，跳转到查询其他在线用户信息的界面
        return render_template("otheruserInfo.html", U=U, username=c_u,restrict=restrict)
    else:
        '''如果没有得到用户名参数u，表明没有用户登录，直接跳转至登录界面'''
        return render_template("login.html")


#修改个人信息
@app.route('/myself/',methods=["POST","GET"])
def myself():
    # 获取url里面传递的用户参数，查询当前用户信息
    c_u = request.args.get("u")
    if c_u:
        if request.method == "GET":
            # 根据用户名查询当前用户
            c_user = User.query.filter(User.username == c_u).first()
            # 将得到的用户信息返回到修改个人信息界面
            return render_template("myself.html", username=c_u, current_user=c_user)
        else:
            '''POST请求，表明当前提交了修改表格，因此修改用户信息'''
            # 从表单里面获取参数信息
            c_user = User.query.filter(User.username == c_u).first()
            c_user.username=request.form.get("username")
            c_user.telephone = request.form.get("telephone")
            c_user.email = request.form.get("email")
            c_user.gender = request.form.get("gender")
            c_user.age = request.form.get("age")
            c_user.city = request.form.get("city")
            c_user.job = request.form.get("job")
            c_user.other = request.form.get("other")
            # 执行
            db.session.commit()
            # 修改信息后，返回登录界面重新进行登录
            return render_template("login.html")
    else:
        return render_template("login.html")

#修改密码
@app.route('/change_password/', methods=["POST", "GET"])
def change_password():
    Tip=""
    #获取传递的参数
    c_u = request.args.get("u")
    if c_u:
        if request.method == "GET":
            return render_template("changepwd.html", username=c_u)
        else:
            '''POST请求，说明用户提交了表单'''
            #从表单中获取原密码、新密码、确认密码
            o_password=request.form.get("o_password")
            o_password=Encode(o_password)
            n_password = request.form.get("n_password")
            a_password = request.form.get("a_password")
            #根据传递的用户名取出用户信息
            c_user = User.query.filter(User.username == c_u).first()
            #判断原密码是不是对的
            if o_password!=c_user.password:
                Tip="原密码错误！"
            else:
                '''判断两次密码是否一致'''
                if n_password!=a_password:
                    Tip="两次密码不一致！"
                else:
                    '''验证通过，修改数据库'''
                    c_user.password=Encode(n_password)
                    #执行
                    db.session.commit()
                    # 需要重新登录
                    return render_template("login.html")
            # 传参、跳转至修改密码界面
            return render_template("changepwd.html", username=c_u, Tip=Tip)



#处理退出
@app.route('/exit/')
def exit():
    # 获取url里面传递的用户参数，得到用户的用户名
    u_name = request.args.get("u")
    # 通过用户名，查询该用户的信息
    c_u = Online.query.filter(Online.username == u_name).first()
    # 删除该用户记录
    db.session.delete(c_u)
    # 执行
    db.session.commit()
    # 此时用户以正常退出，跳转至登录界面
    return render_template("login.html")

if __name__ == '__main__':
    '''app运行'''
    app.run(debug=True)
