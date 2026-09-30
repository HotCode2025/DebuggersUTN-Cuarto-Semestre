package UTN.presentacion;

import UTN.conexion.Conexion;
import UTN.datos.EstudianteDAO;
import UTN.dominio.Estudiante;

import java.util.Scanner;

public class SistemaEstudiantesApp{
    static void main() {
        var salir = false;// recordar que esto ya se hizo antes
        var consola = new Scanner(System.in); //para leer informacion de la consola
        //Se crea una instancia de la clase servicio, esto lo hacemos fuera del ciclo.
        var estudianteDao = new EstudianteDAO();//esta instancia debe hacerse una vez
        while (!salir){
            try{
                mostrarMenu();
                salir = ejecutarOpciones(consola,estudianteDao); //Este arroja una exception. este sera el metodo que devolvera un booleano.
            }catch (Exception e){
                System.out.println("Ocurrió un error al ejecutar la operacion: "+e.getMessage());
            }
        }//fin while
    }//fin main

    private static void mostrarMenu(){
        System.out.print("""
                ******* SISTEMA DE ESTUDIANTES *******
                1. Listar Estudiantes
                2. Buscar Estudiantes
                3. Agregar Estudiantes
                4. Modificar Estudiantes
                5. Eliminar Estudiantes
                6. Salir
                Elige una opción: 
                """);
    }
    //Metodo para ejecutar las opciones, va a regresar un booleano, ya que es el que puede
    // modificar la variable salir, si es verdadero termina el ciclo, sino lo recorre.
    private static boolean ejecutarOpciones(Scanner consola, EstudianteDAO estudianteDAO){
        var opcion = Integer.parseInt(consola.nextLine());
        var salir = false;

        switch (opcion){
            case 1 ->{ //Listar estudiantes
                System.out.println("Listado de Estudiantes: ");
                //no muestra la info, solo la recupera y regresa una lista
                var estudiantes = estudianteDAO.listarEstudiantes(); //recibe el listado
                //vamos a iterar cada objeto de tipo estudiante
                estudiantes.forEach(System.out::println); //para imprimir la lista
            }//fin caso 1
            case 2 ->{ //buscar estudiantes por id
                System.out.println("Introduce el id estudiante a buscar: ");
                var idEstudiante = Integer.parseInt(consola.nextLine());
                var estudiante = new Estudiante(idEstudiante);
                var encontrado = estudianteDAO.buscarEstudiantePorId(estudiante);
                if (encontrado)
                    System.out.println("Estudiante encontrado: "+ estudiante);
                else
                    System.out.println("Estudiante no encontrado: "+estudiante);
            }//fin caso 2
            case 3 -> { // Agregar estudiante
                System.out.println("Agregar estudiante: ");
                System.out.println("Nombre: ");
                var nombre = consola.nextLine();
                System.out.println("Apellido: ");
                var apellido = consola.nextLine();
                System.out.println("Telefono: ");
                var telefono = consola.nextLine();
                System.out.println("Email: ");
                var email = consola.nextLine();
                // crear objeto estudiante (sin id)
                var estudiante = new Estudiante(nombre,apellido,telefono,email);
                var agregado = estudianteDAO.agregarEstudiante(estudiante);
                if (agregado)
                    System.out.println("Estudiante agregado: "+estudiante);
                else
                    System.out.println("Estudiante no agregado: "+estudiante);
            } //fin caso 3
            case 4 ->{ //modificar estudiante
                System.out.println("Modificar Estudiante: ");
                // Aqui lo primero es especificar cual es el id del objeto a modificar
                System.out.println("Id Estudiante: ");
                var idEstudiante = Integer.parseInt(consola.nextLine());
                System.out.print("Nombre: ");
                var nombre = consola.nextLine();
                System.out.println("Apellido: ");
                var apellido = consola.nextLine();
                System.out.println("Telefono: ");
                var telefono = consola.nextLine();
                System.out.println("Email: ");
                var email = consola.nextLine();
                //crear el objeto estudiante a modificar
                var estudiante =
                        new Estudiante(idEstudiante,nombre,apellido,telefono,email);
                var modificado = estudianteDAO.modificarEstudiante(estudiante);
                if (modificado)
                    System.out.println("Estudiante modificado: "+ estudiante);
                else
                    System.out.println("Estudiante No Modificado: "+estudiante);
            }//fin del caso 4
            case 5 -> {//Eliminar estudiante
                System.out.println("Eliminar estudiante: ");
                System.out.println("Id Estudiante: ");
                var idEstudiante = Integer.parseInt(consola.nextLine());
                var estudiante = new Estudiante(idEstudiante);
                var eliminado = estudianteDAO.eliminarEstudiante(estudiante);
                if (eliminado)
                    System.out.println("Estudiante eliminado: "+estudiante);
                else
                    System.out.println("Estudiante No eliminado: "+estudiante);
            }//fin del caso 5
            case 6 ->{//salir
                System.out.println("¡Hasta Pronto!");
                salir = true;
            }//fin caso 6
            default -> System.out.println("Opción no reconocida. Ingrese otra opción.");
        }//Fin Switch
        return salir;
    }
}//fin clase


//import UTN.conexion.Conexion;


//public class SistemaEstudiantesApp {
 //   public static void main(String[] args) {
   //     var conexion = Conexion.getConnection();
     //   if (conexion != null)
       //     System.out.println("Conexión Exitosa: "+conexion);
        //else
         //   System.out.println("Error al conectarse:");
   // }//fin main
//}//fin de clase


