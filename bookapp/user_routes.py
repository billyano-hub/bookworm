import random,string
import json,requests
from functools import wraps
from flask import render_template,request,abort,redirect,flash, make_response,url_for,session
from werkzeug.security import generate_password_hash,check_password_hash
#local imports
from bookapp import app,csrf,mail,Message
from bookapp.models import db,Book,User,Category,State,Lga,Reviews,Donation
from bookapp.forms import *

def login_required(f):
    @wraps(f)#this ensures that details(meta data) about the original function f, that is being decorated is
    def login_check(*args,**kwargs):
        if session.get("userloggedin") != None:
            return f(*args,**kwargs)
        else:
            flash("Access denied")
            return redirect("/login")
    return login_check

@app.route("/sendmail/")
def send_email():
    file=open('requirements.txt')
    msg =Message(subject="Test Email From Bookworm",sender="Adding Heading to Email From Bookworm ",recipients=["billymoney4ever@gmail.com"])
    msg.html="""<h1>Welcome Home!</h1><img src="https://www.google.com/url?sa=i&url=https%3A%2F%2Ftimesofindia.indiatimes.com%2Ftravel%2Fdestinations%2Fparis-in-pictures%2Fphotostory%2F45454098.cms&psig=AOvVaw3k7mKQUTlyPn1CCjuT8kT2&ust=1695392460463000&source=images&cd=vfe&opi=89978449&ved=0CBAQjRxqFwoTCODtqaHzu4EDFQAAAAAdAAAAABAE"><hr>"""
    msg.attach("saved_as.txt","application/text",file.read())
    mail.send(msg)
    return "done"

def generate_string(howmany):
    x=random.sample(string.digits,howmany)
    return ''.join(x)

@app.route('/donate', methods=['POST','GET'])
@login_required
def donate():
    donform=DonationForm()
    if request.method=='GET':
        deets=db.session.query(User).get(session['userloggedin'])
        return render_template("user/donate.html", donform=donform,deets=deets)
    else:
        if donform.validate_on_submit():
            amt=int(donform.amt.data) * 100
            donor=donform.fullname.data
            email=donform.email.data
            #generate a transaction reference for this transaction
            ref ='BW'+ str(generate_string(8))
            donation=Donation(don_amt=amt,don_userid=session['userloggedin'],don_email=email,don_fullname=donor,don_status='pending',don_refno=ref)
            db.session.add(donation)
            db.session.commit()
            #save the reference no in session
            session['trxno']=ref
            #redirect to a configuration page
            return redirect("/confirm_donation")
        else:
            deets=db.session.query(User).get(session['userloggedin'])
            return render_template('user/donate.html', donform=donform, deets=deets)
@app.route("/initialize/paystack/")     
@login_required
def initialize_paystack():
    deets=User.query.get(session['userloggedin'])
    #transaction details
    refno=session.get('trxno')
    transaction_deeets=db.session.query(Donation).filter(Donation.don_refno==refno).first()
    #make a curl request to the paystack endpoint
    url="https://api.paystack.co/transaction/initialize"
   
    headers={"Content-Type": "application/json","Authorization": "Bearer sk_test_a2bfb4bcb2b9d3b06b903106e7d27a264a6a1daf"}
    data={'email':deets.user_email, "amount": transaction_deeets.don_amt,"reference":refno}
    response=requests.post(url,headers=headers,data=json.dumps(data))
    #extract json from the response coming from paystack
    rspjson=response.json()
    if rspjson['status'] ==True:
        redirectURL =rspjson['data']['authorization_url']
        return redirect(redirectURL)#paystack payment page will load
    else:
        flash("Please complete the form again")
        return redirect('/donate')
@app.route("/landing")
@login_required
def landing_page():
    refno=session.get('trxno')
    transaction_deeets=db.session.query(Donation).filter(Donation.don_refno==refno).first()
    url="https://api.paystack.co/transaction/verify/"+transaction_deeets.don_refno
   
    headers={"Content-Type": "application/json","Authorization": "Bearer sk_test_a2bfb4bcb2b9d3b06b903106e7d27a264a6a1daf"}
    response=requests.get(url,headers=headers)
    rspjson=json.loads(response.text)
    #extract json from the response coming from paystack
    if rspjson['status'] ==True:
        paystatus =rspjson['data']['gateway_response']
        transaction_deeets.don_status='paid'
        db.session.commit()
        return redirect('/dashboard')#paystack payment page will load
    else:
        flash("payment failed")
        return redirect('/reports')
    return rspjson




@app.route('/confirm_donation/')
@login_required
def confirm_donation():
    """We want to display the details of the transaction saved from previous page"""
    deets=db.session.query(User).get(session['userloggedin'])
    if session.get('trxno')==None:#means they are visiting here directly
        flash('please Complete this form', category='error')
        return redirect('/donate',deets=deets)
    else:
        donation_deets=Donation.query.filter(Donation.don_refno==session['trxno']).first()
        return render_template('user/donation_confirmation.html',donation_deets=donation_deets,deets=deets)





@app.route("/ajaxopt/",methods=["POST","GET"])
def ajax_options():
    cform=ContactForm()
    if request.method=='GET':
        msg='{"messege":"Not submitted successfully","bsclass"="btn btn-danger"}'
        return render_template('user/ajax_options.html',cform=cform)
    else:
        msg2='{"message":"Submitted", "bsclass=btn btn-success"}'
        email=request.form.get('email')
    return json.dumps(msg,msg2)





@app.route("/contact/")
def ajax_contact():
    data="I am a string coming from the server"
    return render_template("user/ajax_test.html",data=data)
@app.route("/dependent/")
def dependent_dropdown():
    states=db.session.query(State).all()
    
    return render_template("user/show_states.html", states=states)

@app.route("/lga/<stateid>")
def load_lgas(stateid):
    records=db.session.query(Lga).filter(Lga.state_id==stateid).all()
    str2return="<select>"
    for r in records:
        optstr =f"<option value='{r.lga_id}'>"+ r.lga_name+"</option>"
        str2return =str2return + optstr
    str2return =str2return + "</select>"
    return str2return






@app.route("/submission/",methods=["POST","GET"])
def ajax_submission():
    """this route wil be visited by ajax silently"""
    user = request.args.get('fullname')
    if user != "" and user != None:
        return f"Thank you {user} for completing the form"
    else:
        return "Please complete the form"
@app.route('/checkusername/')
def checkusername():
    mail=request.args.get('email')
    u=db.session.query(User).filter(User.user_email==mail).first()
    if u:
        return "email is taken"
    else:
        return 'Email is okay,go ahead pls'


@app.route("/favourite")
def favourite_topics():
    bootcamp={'Name':'Olusegun','topics':['html','css','python']}
    category=[]
    cats=db.session.query(Category).all()
    # for c in cats:
    #     category.append(c.cat_name)
    category=[c.cat_name for c in cats]
    return json.dumps(category)
    #To use login_required, place it after the route decorator over any route that needs authentication
@app.route("/profile", methods=["GET","POST"])
@login_required
def edit_profile():
    id= session.get("userloggedin")
    userdeets=db.session.query(User).get(id)
    pform =ProfileForm()
    if request.method=="GET":
        return render_template('user/edit_profile.html',pform=pform,userdeets=userdeets)
    else:
        if pform.validate_on_submit():
             fullname=request.form.get('fullname')
             userdeets.user_fullname=fullname
             db.session.commit()
             flash("Profile Updated")
             return redirect(url_for("dashboard"))
        else:
            return render_template("user/edit_profile.html",pform=pform,userdeets=userdeets)
@app.route("/changedp/", methods=["GET","POST"])
@login_required
def changedp():
    id = session.get('userloggedin')
    userdeets=db.session.query(User).get(id)
    dpform=DpForm()
    if request.method=="GET":
        return render_template("user/changedp.html",dpform=dpform,userdeets=userdeets)
    else:#form is being submitted
        if dpform.validate_on_submit():
            pix=request.files.get('dp')
            filename=pix.filename
            pix.save(app.config['USER_PROFILE_PATH']+filename)
            userdeets.user_pix=filename
            db.session.commit()
            flash("Profile picture updated",category="info")
            return redirect(url_for("dashboard"))

        else:
            return render_template("user/changedp.html",dpform=dpform,userdets=userdeets)
        
@app.route("/viewall/")
def viewall():
   books=db.session.query(Book.book_status=="1").all()
   return render_template("user/viewall.html",books=books)
@app.route("/logout")
def logout():
    if session.get('userloggedin')!=None:
        session.pop('userloggedin',None)
    return redirect("/")
@app.route("/dashboard")
def dashboard():
    if session.get('userloggedin') !=None:
        id =session.get('userloggedin')
        userdeets=User.query.get(id)
        userdetails=User.query.get(id)

        return render_template('user/dashboard.html',userdetails=userdetails,userdeets=userdeets)
    else:
        flash("You need to login to access this page")
        return redirect("/login")
@app.route("/login/", methods=['POST','GET'])
def login():
    if request.method=="GET":
        return render_template('user/loginpage.html')
    else:
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        deets=db.session.query(User).filter(User.user_email==email).first()
        if deets != None:
            hashed_pwd =deets.user_pwd
            if check_password_hash(hashed_pwd,pwd)==True:
                session['userloggedin']=deets.user_id
                return redirect('/dashboard')
            else:
                flash('Invalid credentials, try again',category="error")
                return redirect('/login/')
        else:
            flash('Invalid cred entials, try again',category='error')
            return redirect('/login/')
@app.route("/register/", methods=['GET','POST'])
def register():
    regform=RegForm()
    if request.method=='GET':
        return render_template('user/signup.html',regform=regform)
    else:
        if regform.validate_on_submit():
             fullname=request.form.get('fullname')
             email=request.form.get('email')
             pwd=request.form.get('pwd')
             
             hashed_pwd=generate_password_hash(pwd)

             
             u =User(user_fullname=fullname,user_email=email,user_pwd=hashed_pwd)
            #  user_pwd=hashed_pwd
             db.session.add(u)
             db.session.commit()
             flash("An account has been created for you.Please login",category="success")
             return redirect(url_for('login'))
        
        else:
            return render_template('user/signup.html',regform=regform)
    # regform=RegForm()
    # return render_template('user/signup.html',regform=regform)

@app.route("/myreviews")
@login_required
def myreviews():
    id=session['userloggedin']
    userdeets=db.session.query(User).get(id)
    return render_template('user/myreviews.html',userdeets=userdeets)
@app.route('/books/details/<id>')
def book_details(id):
    book=Book.query.get_or_404(id)
    
    return render_template("user/reviews.html",book=book)

@app.route('/submit_review/', methods=["POST"])
def submit_review():
    title=request.form.get("title")
    content=request.form.get("content")
    userid=session['userloggedin']
    book=request.form.get('book')
    br=Reviews(rev_title=title, rev_text=content,rev_userid=userid,rev_bookid=book)
    db.session.add(br)
    db.session.commit()

    retstr=f"""<article class="blog-post">
        <h5 class="blog-post-title">{title}</h5>
        <p class="blog-post-meta">Reviewed just now<a href="#">{br.reviewby.user_fullname}</a></p>

        <p>{content}</p>
        <hr> 
      </article>"""
    return retstr



@app.route("/")
def home_page():
    books=db.session.query(Book).filter(Book.book_status=="1").limit(4).all()
    #connect to the port http://127.0.0.1:5000/api/v1.0/listall to collect data of books
    #pass it to the template and display on the template
    try:
        response =requests.get('http://127.0.0.1:5000/api/v1.0/listall') #import requests
        rsp= json.loads(response.text) #response.json()
    except:
        rsp=None #f the server is unreachable
    return render_template("user/home_page.html",books=books,rsp=rsp)
@app.after_request
def after_request(response):
    #To solve he problem of loggedout user's details being cached in the browser
    response.headers['cache-control']='no-cache,no-store, must-revalidate'
    return response

