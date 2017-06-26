FROM python:3.6.1

WORKDIR /st0ckbot
ADD requirements.txt /st0ckbot
RUN pip install -r requirements.txt
RUN errbot --init
RUN rm -rf /st0ckbot/config.py /st0ckbot/plugins
ADD . /st0ckbot
CMD ["errbot"]