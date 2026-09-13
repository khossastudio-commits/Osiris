FROM smartbugs/osiris:d1ecc37

WORKDIR /root

# Reuse the published legacy Osiris toolchain instead of rebuilding
# Ubuntu 16.04, Python 2, solc 0.4.21, evm 1.8.3 and Z3 from source.
COPY osiris /root/osiris
COPY tests /root/tests
COPY datasets/CVEs /root/datasets/CVEs
COPY datasets/SimpleDAO /root/datasets/SimpleDAO
COPY server.py /root/server.py

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "/root/server.py"]
