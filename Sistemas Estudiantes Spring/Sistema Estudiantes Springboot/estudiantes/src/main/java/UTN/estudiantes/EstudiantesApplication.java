package UTN.estudiantes;

import UTN.estudiantes.servicio.EstudianteServicio;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import UTN.estudiantes.modelo.Estudiantes2026;

import java.util.List;
import java.util.Scanner;


@SpringBootApplication
public class EstudiantesApplication implements CommandLineRunner {
	@Autowired
	private EstudianteServicio estudianteServicio;
	private static final Logger logger = LoggerFactory.getLogger(EstudiantesApplication.class);

	String nl = System.lineSeparator();


	public static void main(String[] args) {
		logger.info("Iniciando la Aplicación");
		// Levantar la fabrica de Spring
		SpringApplication.run(EstudiantesApplication.class, args);
		logger.info("Aplicación Finalizada");
	}

	@Override
	public void run(String... args) throws Exception {
		logger.info(nl + "Ejecutando el método run de Spring." + nl);
		var salir = false;
		var consola = new Scanner(System.in);
		while (!salir) {
			mostrarMenu();
			salir = ejecutarOpciones(consola);
			logger.info(nl);
		}//fin del ciclo while
	}
	private void mostrarMenu(){
		//logger.info(nl);
		logger.info("""
				******* SISTEMA DE ESTUDIANTES *******
				1. LISTAR ESTUDIANTES
				2. BUSCAR ESTUDIANTES
				3. AGREGAR ESTUDIANTES
				4. MODIFICAR ESTUDIANTES
				5. ELIMINAR ESTUDIANTES
				6. SALIR
				ELIJA UNA OPCION:""");
		}
		private boolean ejecutarOpciones(Scanner consola){
			var opcion = Integer.parseInt(consola.nextLine());
			var salir = false;
			switch (opcion){
				case 1 ->{//Listar estudiantes
					logger.info(nl+"Listado de estudiantes: "+nl);
					List<Estudiantes2026> estudiantes = estudianteServicio.listarEstudiantes();
					estudiantes.forEach((estudiante -> logger.info(estudiante.toString()+nl)));
				}
				case 2 ->{//Buscar estudiante por Id
					logger.info("Digite el id estudiante a buscar: ");
					var idEstudiante = Integer.parseInt(consola.nextLine());
					Estudiantes2026 estudiante = estudianteServicio.buscarEstudiantePorId(idEstudiante);
					if(estudiante != null)
						logger.info("Estudiante encontrado: "+estudiante+nl);
					else
						logger.info("Estudiante no encontrado: "+estudiante+nl);
				}
				case 3 -> {//Agregar estudiante
					logger.info("Agregar estudiante: "+nl);
					logger.info("Nombre: ");
					var nombre = consola.nextLine();
					logger.info("Apellido: ");
					var apellido = consola.nextLine();
					logger.info("Telefono: ");
					var telefono = consola.nextLine();
					logger.info("Email: ");
					var email = consola.nextLine();
					//Crear el objeto estudiante sin el id
					var estudiante = new Estudiantes2026();
					estudiante.setNombre(nombre);
					estudiante.setApellido(apellido);
					estudiante.setTelefono(telefono);
					estudiante.setEmail(email);
					estudianteServicio.guardarEstudiante(estudiante);
					logger.info("Estudiante Agregado: "+estudiante+nl);
				}
				case 4 -> {//modificar estudiante
					logger.info("Modificar estudiante: "+nl);
					logger.info("Ingrese el id estudiante: "+nl);
					var idEstudiante = Integer.parseInt(consola.nextLine());
					//buscamos el estudiante a modificar
					Estudiantes2026 estudiante= estudianteServicio.buscarEstudiantePorId(idEstudiante);
					if(estudiante != null){
						logger.info("Nombre: ");
						var nombre = consola.nextLine();
						logger.info("Apellido: ");
						var apellido = consola.nextLine();
						logger.info("Telefono: ");
						var telefono = consola.nextLine();
						logger.info("Email: ");
						var email = consola.nextLine();
						estudiante.setNombre(nombre);
						estudiante.setApellido(apellido);
						estudiante.setTelefono(telefono);
						estudiante.setEmail(email);
						estudianteServicio.guardarEstudiante(estudiante);
						logger.info("Estudiante Modificado: "+estudiante+nl);
					}
				}
				case 5 ->{//Eliminar estudiante
					logger.info("Eliminar estudiante: "+nl);
					logger.info("Digite el id estudiante: ");
					var idEstudiante = Integer.parseInt(consola.nextLine());
					//buscamos el id estudiante a eliminar
					var estudiante = estudianteServicio.buscarEstudiantePorId(idEstudiante);
					if(estudiante != null){
						estudianteServicio.eliminarEstudiante(estudiante);
						logger.info("Estudiante Eliminado: "+estudiante+nl);
					}else
						logger.info("Estudiante No encontrado con id: "+estudiante+nl);
				}
				case 6 ->{//salir
					logger.info("¡Hasta Pronto!"+nl+nl);
					salir = true;
				}
                default -> logger.info("Opción no reconocida: "+ opcion+nl);
			}//fin switch
			return salir;
		}//fin metodo ejecutarOpciones
	}//fin clase estudiantesapplication

