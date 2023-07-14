FROM python:alpine3.17

WORKDIR ./app
RUN pip install flask
RUN pip install requests
RUN pip install flask_restful
COPY mealserver.py .
EXPOSE 8000
ENV FLASK_APP=mealserver.py
ENV FLASK_RUN_PORT=8000
CMD ["flask", "run", "--host=0.0.0.0"]