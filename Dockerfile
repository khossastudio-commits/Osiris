FROM smartbugs/osiris:latest

WORKDIR /root

# Use the code from this repository while reusing the prebuilt legacy
# Osiris toolchain (Python 2, solc 0.4.21, evm 1.8.3 and Z3 4.6.0).
COPY osiris /root/osiris
COPY tests /root/tests
COPY datasets/CVEs /root/datasets/CVEs
COPY datasets/SimpleDAO /root/datasets/SimpleDAO
COPY server.py /root/server.py

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "/root/server.py"]
