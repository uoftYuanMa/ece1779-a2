from flask import render_template, url_for, session, redirect, request, flash
from flaskr import app
from flaskr import db
from flaskr.models import AutoScalingConfig
from flaskr import forms
from datetime import datetime
import traceback
import json

@app.route('/configure')
def configure():
    user = session['user'] if 'user' in session else None
    if not user:
        return redirect(url_for('login'))
    else:
        try:
            form = forms.ConfigForm()
            # AutoAcalingConifg.query...
            #   one config, order by timestamp
            #


            values={
                "cpu_grow": 3,
                "cpu_shrink": 2,
                "ratio_expand": 2,
                "ratio_shrink": 0.5
            }
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

                # 2. add into cpu_grow. generate current datetime

                flash("Configuration has been updated!", "success")
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

def configure_auto_scaling():
    """
    :return: latest configure info
    """