import dns.exception
import dns.resolver
import smtplib
import os
import random
import ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from string import Template
from difflib import get_close_matches
from flask import render_template

class verify_email:

    def verify_domain(self, email):
        try:
            domain = email.split('@')[-1]
            answers = dns.resolver.resolve(domain, 'MX')
            return True
        
        except dns.resolver.NXDOMAIN: 
            print("agarre el error1")  
            return False
        except dns.resolver.NoAnswer:
            print("agarre el error1")  
            return False
        except dns.resolver.Timeout:
            print("El tiempo de espera agotado al consultar el dominio")
            return False
        except dns.exception.DNSException as err:
            print(f"Error generico de DNS: {err}")
            return False
        except Exception as err:
            print(f"Error al verificar dominio: {err}")
            return False
    

    def suggest_domain(self, email):
        known_domains = ["gmail.com", "yahoo.com", "hotmail.com"]
        domain = email.split('@')[-1]
        suggestions = get_close_matches(domain, known_domains)
        return suggestions
    
    def send_email(self, email, username):
        
        print("recibio correo y nombre de usuario")
        
        verification_code = random.randint(100000, 999999)

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "email_template.html")
        
        with open(path, 'r') as file:
            template = Template(file.read())
    
        content = template.substitute(username = username, verification_code = verification_code)

        password = os.getenv("PASSWORD")
        
        if not password:
            print ("No se encontro la contraseña")
            return 
                
        sender = "peertopeerverificacion@gmail.com"
        addressee = (f"{email}")
        subject = "Correo de Verificación"
                        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = addressee
        msg.attach(MIMEText(content, 'html'))

        context = ssl.create_default_context()
        
        if not self.verify_domain(email):
            print("el correo no es valido")
            suggestions = self.suggest_domain(email)
            
            if suggestions:
                print(f"Quisiste decir {email.split('@')[0]}@{suggestions[0]}?")

            return render_template("inicio.html")
            
        else:

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as server:
                    server.login(sender, password)
                    result = server.sendmail(sender, addressee, msg.as_string())
                    
                    if result:
                        for recipient, error in result.items():
                            print(f"Eror al enviar a {recipient}: {error}")
                            
                    else: 
                        print("El correo fue enviado exitosamente")
                        return render_template("v_e_r.html", verification_code)
                    
            except smtplib.SMTPRecipientsRefused:
                print(f"El destinatario {addressee} ha sido rechazado")
            except smtplib.SMTPAuthenticationError:
                print("Error de autenticación: Verifica la contraseña o la configuración de la cuenta")
            except Exception as err:
                print(f"Error inesperado al enviar el correo: {err}")