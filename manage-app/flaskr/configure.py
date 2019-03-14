from flask import render_template, url_for, session, redirect, request, flash
from flaskr import app
from flaskr import db
from flaskr.models import AutoScalingConfig
from flaskr import forms
from datetime import datetime
import traceback
import json
from sqlalchemy import desc


@app.route('/configure')
def configure():
    user = session['user'] if 'user' in session else None
    if not user:
        return redirect(url_for('login'))
    else:
        try:
            form = forms.ConfigForm()
            #   one config, order by timestamp
            values=configure_auto_scaling_info()
            # values = {
            #     "cpu_grow": 3,
            #     "cpu_shrink": 2,
            #     "ratio_expand": 2,
            #     "ratio_shrink": 0.5
            # }
            return render_template('configure.html', form=form, values=values)
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            return render_template('error.html', msg='something goes wrong~')

@app.route('/configure_auto_scaling', methods=['GET', 'POST'])
def configure_auto_scaling():
    """
    request keys: cpu_grow, cpu_shrink, ratio_expand, ratio_shrink
    :return: msg: str
    """
    user = session['user'] if 'user' in session else None
    if not user:
        return redirect(url_for('login'))
    else:
        try:
            form = forms.ConfigForm()
            if form.validate_on_submit():
                cpu_grow = form.cpu_grow.data
                cpu_shrink = form.cpu_shrink.data
                ratio_expand = form.ratio_expand.data
                ratio_shrink = form.ratio_shrink.data
                # 1. check input
                if isinstance(cpu_grow, int)&cpu_grow<=10&cpu_grow>0:
                    if isinstance(cpu_shrink, int)&cpu_shrink<=10&cpu_shrink>0:
                        if cpu_grow>cpu_shrink:
                            if isinstance(ratio_expand, float)&(ratio_expand<=10)&(ratio_expand>=1):
                                if isinstance(ratio_shrink, float)&(ratio_shrink<1)&(ratio_shrink>0):
                                    # 2. add into cpu_grow. generate current datetime
                                    value = AutoScalingConfig(cpu_grow=cpu_grow, cpu_shrink=cpu_shrink,
                                                              ratio_expand=ratio_expand, ratio_shrink=ratio_shrink,
                                                              timestamp=datetime.now())
                                    db.session.add(value)
                                    db.session.commit()
                                    flash("Configuration has been updated!", "success")
                                else: flash("ratio_shrink: Not a valid floating point value,"
                                            "Float with 3 digits", "error")
                            else: flash("ratio_expand: Not a valid floating point value,"
                                        "Float with 3 digits", "error")
                        else: flash("cpu_grow should not lower than cpu_shrink","error")
                    else: flash("cpu_shrink: Not a valid integer value,Integer with 3 digits", "error")
                else: flash("cpu_grow: Not a valid integer value,Integer with 3 digits", "error")

            else:
                if form.cpu_grow.errors:
                    flash("cpu_grow: " + ",".join(form.cpu_grow.errors), "error")
                elif form.cpu_shrink.errors:
                    flash("cpu_shrink: " + ",".join(form.cpu_shrink.errors), "error")
                elif form.ratio_expand.errors:
                    flash("ratio_expand: " + ",".join(form.ratio_expand.errors), "error")
                elif form.ratio_shrink.errors:
                    flash("ratio_shrink: " + ",".join(form.ratio_shrink.errors), "error")
                else: pass

            return redirect(url_for('configure'))

        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            return render_template('error.html', msg='something goes wrong~')

def configure_auto_scaling_info(): #这里的函数名和上一个重复了，我加了个info
    #return: latest configure info
    return AutoScalingConfig.query.order_by(desc(AutoScalingConfig.timestamp)).first()