import os
from supabase import create_client, Client
import time

class db_habdler:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.tabla = "users"
        self.supabase :Client = create_client(self.url, self.key)
    
    def get_all_users(self):
        response = self.supabase.table(self.tabla).select("*").execute()
        return response.data

    def does_rfid_edxis(self, rfid:str):
        response = self.supabase.table(self.tabla).select("*").eq("uid", rfid).execute()
        print("does_rfid_exist",response.data)
        #return true or false
        return response.data != []
    
    def enough_money(self, rfid:str):
        amount = 3
        response = self.supabase.table(self.tabla).select("saldo").eq("uid", rfid).execute()
        print("enough_money",response.data)
        return response.data[0]["saldo"],response.data[0]["saldo"] >= amount
    
    
    
    def entrance(self, rfid:str):
        money, flag = self.enough_money(rfid)  
        if flag:
            money -= 3
            #get current time in day, month, year, hour, minute, second
            current_time = time.localtime()
            formatted_time = time.strftime("%d-%m-%Y %H:%M:%S", current_time)
            print(formatted_time)
            response = self.supabase.table(self.tabla).update({"saldo":money, "ultima_entrada": str(formatted_time)}).eq("uid", rfid).execute()
            print(response.data)
            
            
            
            return response.data != []
        else:
            print("Not enough money")
            return False
        
    
            
    def login(self, name:str, password:str):
        #its just a simulation of login, the email and password are in the table usuarios
        response = self.supabase.table("admins").select("*").eq("nombre", name).eq("password", password).execute()
        print(response.data)
        return response.data != []
        
     #activa significa que esta adentro, inactiva que esta afuera   
    def add_new_user(self, input: dict):
        try:
            rfid = input["uid"]
            name = input["nombre"]
            apelido = input["apellido"]
            id = input["id"]
            password = ""
            saldo = 10
            activa = False
            model = input["model"]
            response = self.supabase.table(self.tabla).insert([{"id":id,"nombre":name,"apellido":apelido,"uid":rfid, "saldo":saldo, "activa":activa, "model":model}]).execute()
            print(response.data)
            return response.data != []
        except Exception as e:
            print(e)
            return False
        
        
        
        
test = db_habdler()
print(test.get_all_users())
print(test.does_rfid_edxis("nhjh2h3jh"))
print(test.login("Admin", "Admin"))
print(test.entrance("nhjh2h3jh"))
mock_user = {
    "uid":"betobeto123",
    "nombre":"test",
    "apellido":"test",
    "id":"10",
    "model":"test"
}
print(test.add_new_user(mock_user))
