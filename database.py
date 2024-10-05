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
            #check if activa = True
            response = self.supabase.table(self.tabla).select("activa").eq("uid", rfid).execute()
            adentro = response.data[0].get("activa",None)
            if adentro:
                print("User is already inside")
                return False
            else:
                money -= 3
                #get current time in day, month, year, hour, minute, second
                current_time = time.localtime()
                formatted_time = time.strftime("%d-%m-%Y %H:%M:%S", current_time)
                user_id = self.supabase.table(self.tabla).select("id").eq("uid", rfid).execute().data[0].get("id",None)
                print(formatted_time)
                response = self.supabase.table(self.tabla).update({"saldo":money, "ultima_entrada": str(formatted_time), "activa": True}).eq("uid", rfid).execute()
                try:
                    self.supabase.table("historial").insert([{"id":int(user_id), "fecha":str(formatted_time),"accion":"entrada", "user_id":int(user_id)}]).execute()
                    print("Historial updated")
                except Exception as e:
                    print(e)
                print(response.data)
                return response.data != []
        else:
            print("Not enough money")
            return False
        
        
        
    def exit(self, rfid:str):
        flag = self.does_rfid_edxis(rfid)
        #if the rfid exists
        if flag:
            #check if activa = True
            response = self.supabase.table(self.tabla).select("activa").eq("uid", rfid).execute()
            adentro = response.data[0].get("activa",None)     
            if  adentro:
                #get current time in day, month, year, hour, minute, second
                current_time = time.localtime()
                formatted_time = time.strftime("%d-%m-%Y %H:%M:%S", current_time)
                print(formatted_time)
                response = self.supabase.table(self.tabla).update({"ultima_salida": str(formatted_time), "activa": False}).eq("uid", rfid).execute()
                user_id = self.supabase.table(self.tabla).select("id").eq("uid", rfid).execute().data[0].get("id",None)
                print(response.data)
                try:
                    self.supabase.table("historial").insert([{"id":int(user_id), "fecha":str(formatted_time),"accion":"salida", "user_id":int(user_id)}]).execute()
                    print("Historial updated")
                except Exception as e:
                    print(e)
                
                return response.data != []
            else:
                print("User is not inside")
                return False
        else:
            print("User does not exist")
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
        
        
        
        
"""test = db_habdler()
print(test.get_all_users())
print(test.does_rfid_edxis("33AF1B12"))
print(test.login("Admin", "Admin"))
print(test.entrance("33AF1B12"))
mock_user = {
    "uid":"betobeto123",
    "nombre":"test",
    "apellido":"test",
    "id":"10",
    "model":"test"
}
print(test.add_new_user(mock_user))
print(test.exit("33AF1B12"))
print(test.entrance("33AF1B12"))
print(test.exit("33AF1B12"))"""