package utn.estudiantes;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import utn.estudiantes.servicio.EstudianteServicio;

import java.util.List;
import java.util.Scanner;
import utn.estudiantes.modelo.Estudiante;

@SpringBootApplication
public class EstudiantesApplication implements CommandLineRunner {

	@Autowired
	private EstudianteServicio estudianteServicio;
	private static final Logger logger =

			LoggerFactory.getLogger(EstudiantesApplication.class);

	String nl = System.lineSeparator();

	public static void main(String[] args) {
		logger.info("Iniciando la aplicación...");
		// Levantar fabrica de Spring
		SpringApplication.run(EstudiantesApplication.class, args);
		logger.info("Aplicación Finalizada!");
	}


	@Override
	public void run(String... args) throws Exception {
		logger.info(nl+"Ejecutando el método run de Spring..."+nl);
		var salir = false;
		var consola = new Scanner(System.in);
		while(!salir){
			mostrarMenu();
			salir = ejecutarOpciones(consola);
			logger.info(nl);
		} //Fin ciclo While

	}

	private void mostrarMenu(){
		//logger.info(nl);
		logger.info(nl + """
    			***** Sistema de Estudiantes *****
    			1. Listar Estudiantes
    			2. Buscar Estudiante
    			3. Agregar Estudiante
    			4. Modificar Estudiante
    			5. Eliminar Estudiante
    			6. Salir""");
		System.out.print("Elija una opción: ");

	}

	private boolean ejecutarOpciones(Scanner consola) {
		var opcion = 0; //Inicializamos la variable en 0 por defecto
		var salir = false;

		try {
			opcion = Integer.parseInt(consola.nextLine());
		} catch (NumberFormatException e) {
			// Si ingresa una letra o un símbolo, el catch atrapa el error
			logger.info(nl + "¡Error! Por favor, ingrese un número válido." + nl);
			return false; // Retornamos false para que el ciclo siga y vuelva a mostrar el menú
		}

		switch (opcion) {
			case 1 -> { //Listar estudiantes
				logger.info(nl+"Listado de estudiantes: " + nl);
				List<Estudiante> estudiantes = estudianteServicio.listarEstudiantes();
				estudiantes.forEach((estudiante -> logger.info(estudiante.toString()+nl)));
			}
			case 2 -> {//Buscar estudiante por id
				System.out.print("Digite el id estudiante a buscar: ");
				var idEstudiante = Integer.parseInt(consola.nextLine());
				Estudiante estudiante =
						estudianteServicio.buscarEstudiantePorId(idEstudiante);
				if(estudiante != null)
					logger.info("Estudiante encontrado: "+ estudiante + nl);
				else
					logger.info("Estudiante NO encontrado: "+ estudiante +nl);
			}
			case 3 -> { //Agregar estudiante
				logger.info("Agregar estudiante: "+nl);

				System.out.print("Nombre: ");
				var nombre = consola.nextLine();

				System.out.print("Apellido: ");
				var apellido = consola.nextLine();

				System.out.print("Telefono: ");
				var telefono = consola.nextLine();

				System.out.print("Email: ");
				var email = consola.nextLine();

				// Crear el objeto estudiante sin el id
				var estudiante = new Estudiante();
				estudiante.setNombre(nombre);
				estudiante.setApellido(apellido);
				estudiante.setTelefono(telefono);
				estudiante.setEmail(email);

				estudianteServicio.guardarEstudiante(estudiante);
				logger.info("Estudiante agregado: "+estudiante+nl);
			}
			case 4 -> { // Modificar estudiante
				logger.info("Modificar estudiante: "+nl);

				System.out.print("Ingrese el id estudiante: ");
				var idEstudiante = Integer.parseInt(consola.nextLine());

				// buscamos el estudiante a modificar
				Estudiante estudiante =
						estudianteServicio.buscarEstudiantePorId(idEstudiante);
				if(estudiante != null){
					System.out.print("Nombre: ");
					var nombre = consola.nextLine();

					System.out.print("Apellido: ");
					var apellido = consola.nextLine();

					System.out.print("Telefono: ");
					var telefono = consola.nextLine();

					System.out.print("Email: ");
					var email = consola.nextLine();

					estudiante.setNombre(nombre);
					estudiante.setApellido(apellido);
					estudiante.setTelefono(telefono);
					estudiante.setEmail(email);

					estudianteServicio.guardarEstudiante(estudiante);
					logger.info("Estudiante modificado: "+estudiante+nl);
				}
				else
					logger.info("Estudiante NO encontrado con el id: " + idEstudiante+nl);
			}
			case 5 -> { //Eliminar estudiante
				logger.info("Eliminar estudiante: "+nl);

				System.out.print("Digite el id estudiante: ");
				var idEstudiante = Integer.parseInt(consola.nextLine());

				// Buscamos el id estudiante a eliminar
				var estudiante = estudianteServicio.buscarEstudiantePorId(idEstudiante);
				if(estudiante != null){
					estudianteServicio.eliminarEstudiante(estudiante);
					logger.info("Estudiante eliminado: "+estudiante+nl);
				}
				else
					logger.info("Estudiante NO encontrado con id: "+idEstudiante+nl);
			}
			case 6 -> { //Salir
				logger.info("Hasta pronto!"+nl+nl);
				salir = true;
			}
			default -> logger.info("Opción no reconocida: "+ opcion+nl);
		}//Fin switch
		return salir;
	} //Fin metodo ejecutarOpciones

} //Fin clase EstudiantesApplication
