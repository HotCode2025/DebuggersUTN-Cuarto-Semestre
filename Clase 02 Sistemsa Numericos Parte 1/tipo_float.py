# Profundizando en el tipo Float
a = 3.0
print(f'a: {a:.2f}') #sirve para achicar numero o agrandar

# Constructor de tipo float -> puede recibir int y str
a = float(10) #Le pasamos un tipo entero (int)
a = float('10')
print(f'a: {a:.2f}')

# Notación exponencial (valores positivos o negativos)
a = 3e5
print(f'a: {a:.2f}') #al numero 3 le agregamos 5 ceros y 2f son dos ceros despues de la coma

#Valores NEGATIVOS
a = 3e-5
print(f'a: {a:.5f}')

# Cualquier calculo que incluye un float, todo cambia a float

a = 4.0 + 5
print(a)
print(type(a))