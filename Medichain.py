from base64 import encode
from crypt import methods
import datetime
import hashlib
import json
from textwrap import indent
from urllib import response
from flask import Flask, jsonify, request, session
from flask_session import Session
from numpy import block
from paramiko import HostKeys

class Medichain:
    
    def __init__(self):
        self.chain = []
        self.create_block(nonce = 1, prevHash = '0', records=[])
    
    def create_block(self, nonce, prevHash, records):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'nonce': nonce,
            'records': records,
            'previous_hash': prevHash
        }
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, prevNonce):
        newNonce = 1
        checkProof = False
        while checkProof is False:
            hashOperation = hashlib.sha256(str(newNonce**2 - prevNonce**2).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof = True
            else:
                checkProof = False
                newNonce += 1
        return newNonce

    def blockHash(self, block):
        encodedBlock = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()

    def is_chain_valid(self, chain):
        if(len(chain)<=1):
            return True

        prevBlock = chain[0]
        for block in chain[1:]:
            if block['previous_hash'] != self.blockHash(prevBlock):
                return False
            prevNonce = prevBlock['nonce']
            newNonce = block['nonce']
            hashOperation = hashlib.sha256(str(newNonce**2 - prevNonce**2).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                return False
            prevBlock = block
        return True


app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

blockchain = Medichain()

@app.route('/get_records', methods=['GET'])
def get_records():
    if 'memPool' not in session:
        session['memPool'] = []

    memPool = session['memPool']
    return jsonify(memPool), 200

@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    doctor = request.args.get('Doctor')
    patient = request.args.get('Patient')
    report = request.args.get('Report')

    record = {
            'Doctor': doctor,
            'Patient': patient,
            'Report': report
        }

    if 'memPool' not in session:
        session['memPool'] = []

    session['memPool'].append(record)
    memPool = session['memPool']

    if(len(memPool) == 5):
        mine_block(memPool)
        session['memPool'] = []

    return jsonify(record), 200

# @app.route('/mine_block', methods=['GET'])
def mine_block(records):
    prevBlock = blockchain.get_previous_block()
    prevNonce = prevBlock["nonce"]
    currNonce = blockchain.proof_of_work(prevNonce)
    prevHash = blockchain.blockHash(prevBlock)
    block = blockchain.create_block(currNonce, prevHash, records)

    response = {
        "message": 'Congratulation on mining a new block',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'nonce': block['nonce'],
        'records': records,
        'previous_hash': block['previous_hash']
    }

    # return jsonify(response)

@app.route('/get_chain', methods=['GET'])
def get_chain():
    memPool = session['memPool']

    response = {
        'chain_length': len(blockchain.chain),
        'chain': blockchain.chain,
        'mem_pool_length': len(memPool),
        'mem_pool': memPool
    }

    return jsonify(response), 200

@app.route('/check_validity', methods=['GET'])
def is_valid():
    isValid = blockchain.is_chain_valid(blockchain.chain)

    if isValid:
        response = {
            'message': 'Alright, The Blockchain is valid'
        }
    else:
        response = {
            'message': 'There\'s something wrong with the chain'
        }
    
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5000)