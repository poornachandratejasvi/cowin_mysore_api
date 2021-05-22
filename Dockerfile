FROM python:3.7.9-slim
RUN mkdir /bd_build
COPY * /bd_build/
RUN mkdir /opt/cowin/
RUN ls /bd_build/
RUN cp /bd_build/cowin.py /opt/cowin/
RUN cp /bd_build/run.sh /opt/cowin/
COPY docker-entrypoint.sh /
RUN apt-get update && apt-get install -y procps
RUN /bd_build/preparebase.sh

RUN chmod +x /docker-entrypoint.sh
RUN rm -rf /bd_build/

#ENTRYPOINT [ "/docker-entrypoint.sh" ]
CMD ["python","-u","/opt/cowin/cowin.py"]

