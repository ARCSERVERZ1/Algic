import pyrebase
import time
import rag

class createBifrsot:

    def __init__(self, user, db , rag):
        self.database = db
        self.user = user
        self.rag = rag
        self.run_bifrost()

    def process_query(self,context , query):
        print(f"Query is {query}")
        res = self.rag.ask(query)
        db.child(self.user).child('response').set(res['output_text'])
        db.child(self.user).child('res_status').set('end')
    def run_bifrost(self):
        while True:
            res_status = db.child(self.user).child('res_status').get()
            if res_status.val() == 'set':
                query = db.child(self.user).child('query').get().val()
                context = db.child(self.user).child('context').get().val()
                db.child(self.user).child('res_status').set('processing')
                self.process_query(context , query)
                print(query)

            time.sleep(0.1)


if __name__ == '__main__':
    firebaseConfig = {
        'apiKey': "AIzaSyAMoENs6AiTkSnAhuHuzwpGFkxeaAhGQB4",
        "authDomain": "aura-bifrost.firebaseapp.com",
        "databaseURL": "https://aura-bifrost-default-rtdb.firebaseio.com",
        "projectId": "aura-bifrost",
        "storageBucket": "aura-bifrost.appspot.com",
        "messagingSenderId": "774636407803",
        "appId": "1:774636407803:web:7710f0dec1c433a1b5d95e",
        "measurementId": "G-F8LXP6ZP1Q"
    }

    firebase = pyrebase.initialize_app(firebaseConfig)
    db = firebase.database()
    rag = rag.rag(["Panisha's AAdhar number is 33459148837"], 'vector-20240731')
    createBifrsot('sanjay', db , rag)
