RUN python --version
COPY . /kirin
RUN pip install -r /kirin/requirements.txt -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

WORKDIR /kirin

EXPOSE 8000

CMD ["python", "main.py"]
