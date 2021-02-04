import ssl
from routes import app


if __name__ == '__main__':
    # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # context.verify_mode = ssl.CERT_REQUIRED
    # context.load_verify_locations('./certs/pnnl_cert.pem')
    # context.load_cert_chain('./certs/server.crt','./certs/server.key')
    app.run(host='0.0.0.0', port=8080, debug=True)