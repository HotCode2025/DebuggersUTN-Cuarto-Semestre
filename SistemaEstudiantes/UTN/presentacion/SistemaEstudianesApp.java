package UTN.presentacion;

import UTN.conexion.Conexion;
import UTN.datos.EstudianteDAO;
import UTN.dominio.Estudiante;

import java.util.Scanner;

public class SistemaEstudianesApp {
    public static void main(String[] args) {
        var salir = false;
        var consola = new Scanner(System.in);
        
        var estudianteDao = new EstudianteDAO();
        
        while (!salir) {
            try {
                mostrarMenu();
                salir = ejecutarOpciones(consola, estudianteDao);
            }
            catch (Exception e) {
                System.out.println("Ocurrio un error el ejecutar la operacion: " + e.getMessage());
            }
        } // Fin while
    } // Fin main
    
    private static void mostrarMenu() {
        System.out.print("""
                         **** Sistema de Estudiantes ****
                          1. Listar Estudiantes
                          2. Buscar Estudiantes
                          3. Agregar Estudiantes
                          4. Modificar Estudiantes
                          5. Eliminar Estudiantes
                          6. Salir
                         Elige una opción: 
                         """);
    }
    
    private static boolean ejecutarOpciones(Scanner consola, EstudianteDAO estudianteDAO) {
        var opcion = Integer.parseInt(consola.nextLine());
        var salir = false;
        switch (opcion) {
            case 1 -> { // Listar estudiantes
                System.out.println("Listado de Estudiantes");
                var estudiantes = estudianteDAO.listarEstudiantes();
                estudiantes.forEach(System.out::println);
            } // Fin case 1
            case 2 -> { // Buscar estudiante por ID
                System.out.println("Buscar Estudiante por ID");
                System.out.println("Ingresa el Id del estudiante a buscar ");
                var idestudiante = Integer.parseInt(consola.nextLine());
                var estudiante = new Estudiante(idestudiante);
                var encontrado = estudianteDAO.buscarEstudiantePorId(estudiante);
                if (encontrado) {
                    System.out.println("Estudiante encontrado: " + estudiante);
                }
                else {
                    System.out.println("Estudiante NO encontrado: " + estudiante);
                }
            } // Fin case 2
            case 3 -> { // Agregar estudiante
                System.out.println("Agregar Estudiantes");
                System.out.print("Nombre: ");
                var nombre = consola.nextLine();
                System.out.print("Apellido: ");
                var apellido = consola.nextLine();
                System.out.print("Telefono: ");
                var telefono = consola.nextLine();
                System.out.print("Email: ");
                var email = consola.nextLine();
                // Crear objeto estudiante sin id
                var estudiante = new Estudiante(nombre, apellido, telefono, email);
                var agregado = estudianteDAO.agregarEstudiante(estudiante);
                if (agregado) {
                    System.out.println("Estudiante agregado: " + estudiante);
                }
                else {
                    System.out.println("Estudiante NO agregado: " + estudiante);
                }
            } // Fin case 3
            case 4 -> { // Modificar un estudiante
                System.out.println("Modificar Estudiantes");
                System.out.print("ID Estudiante: ");
                var idestudiante = Integer.parseInt(consola.nextLine());
                System.out.print("Nombre: ");
                var nombre = consola.nextLine();
                System.out.print("Apellido: ");
                var apellido = consola.nextLine();
                System.out.print("Telefono: ");
                var telefono = consola.nextLine();
                System.out.print("Email: ");
                var email = consola.nextLine();
                // Crear objeto estudiante a modificar
                var estudiante = new Estudiante(idestudiante, nombre, apellido, telefono, email);
                var modificado = estudianteDAO.modificarEstudiante(estudiante);
                if (modificado) {
                    System.out.println("Estudiante modificado: " + estudiante);
                }
                else {
                    System.out.println("Estudiante NO modificado: " + estudiante);
                }
            } // Fin case 4
            case 5 -> { // Eliminar un estudiante
                System.out.println("Eliminar Estudiantes");
                System.out.print("ID Estudiante: ");
                var idestudiante = Integer.parseInt(consola.nextLine());
                // Crear objeto estudiante a modificar
                var estudiante = new Estudiante(idestudiante);
                var eliminado = estudianteDAO.eliminarEstudiante(estudiante);
                if (eliminado) {
                    System.out.println("Estudiante eliminado: " + estudiante);
                }
                else {
                    System.out.println("Estudiante NO eliminado: " + estudiante);
                }
            } // Fin case 5
            case 6 -> { // Salir
                System.out.println("Hasta pronto");
                salir = true;
            } // Fin case 6
            default -> {
                System.out.println("Opcion no valida");
            }
        } // Fin switch
        return salir;
    }
}

