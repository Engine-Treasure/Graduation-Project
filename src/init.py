# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-04-10"


from celery import Celery


app = Celery("Graduation Project",
             broker="ampq://",
            backend="rpc://",
             include=[
                 "controller"
             ],)

app.config_from_object("celeryconfig")


if __name__ == "__main__":
    app.start()