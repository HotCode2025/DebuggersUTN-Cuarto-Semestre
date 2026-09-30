package UTN.datos;

import UTN.conexion.Conexion;
import UTN.dominio.Estudiante;

import static UTN.conexion.Conexion.getConnection;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;


public class EstudianteDAO {
    //Método listar
    public List<Estudiante> listarEstudiantes(){
        List<Estudiante> estudiantes = new ArrayList<>();
        //Creamos algunos objetos que son necesarios para comunicarnos con la base de datos.
        PreparedStatement ps; //prepara la sentencia de sql
        ResultSet rs; //permite almacenar el resultado obtenido de la base de datos
        //Creamos un objeto de tipo conexión

        Connection con = getConnection();
        String sql = "SELECT * FROM estudiantes2026 ORDER BY idestudiantes2026";
        try{
            ps = con.prepareStatement(sql);
            rs = ps.executeQuery();
            while (rs.next()){
                var estudiante = new Estudiante();
                estudiante.setIdEstudiante(rs.getInt("idestudiantes2026"));
                estudiante.setNombre(rs.getString("nombre"));
                estudiante.setApellido(rs.getString("apellido"));
                estudiante.setTelefono(rs.getString("telefono"));
                estudiante.setEmail(rs.getString("email"));
                //Falta agregarlo a la lista
                estudiantes.add(estudiante);
            }

        } catch(Exception e){
            System.out.println("Ocurrio un error al seleccionar los datos: "+e.getMessage());
        }
        finally{
            try{
                con.close();
            }
            catch(Exception e){
                System.out.println("Ocurrió un error al cerrar la conexión: "+e.getMessage());
            }
        }//fin finally
        return estudiantes;
    }//fin metodo listar

    // Metodo por id ->> find by ID
    public boolean buscarEstudiantePorId(Estudiante estudiante){
        PreparedStatement ps;
        ResultSet rs;
        Connection con = getConnection();
        String sql = "SELECT * FROM estudiantes2026 WHERE idestudiantes2026=?";
        try{
            ps = con.prepareStatement(sql);
            ps.setInt(1, estudiante.getIdEstudiante());
            rs = ps.executeQuery();
            if(rs.next()){
                estudiante.setNombre(rs.getString("nombre"));
                estudiante.setApellido(rs.getString("apellido"));
                estudiante.setTelefono(rs.getString("telefono"));
                estudiante.setEmail(rs.getString("email"));
                return true; //Se encontro un registro
            }//Fin if

        }catch (Exception e) {
            System.out.println("Ocurrió un error al buscar estudiante: " + e.getMessage());
        }//Fin catch
        finally {
            try {
                con.close();
            }catch(Exception e){
                System.out.println("Ocurrio un error al cerrar la conexión: "+e.getMessage());
            }//fin catch
        }//fin finally
        return false;
    }

    // Método agregar un nuevo estudiante
    public boolean agregarEstudiante(Estudiante estudiante){
        PreparedStatement ps;
        Connection con = getConnection();
        String sql = "INSERT INTO estudiantes2026 (nombre, apellido, telefono, email) VALUES (?,?,?,?)";
        try{
            ps = con.prepareStatement(sql);
            ps.setString(1,estudiante.getNombre());
            ps.setString(2,estudiante.getApellido());
            ps.setString(3, estudiante.getTelefono());
            ps.setString(4,estudiante.getEmail());
            ps.execute();
            return true;

        }catch (Exception e){
            System.out.println("Ocurrió un error al agregar el nuevo estudiante: "+e.getMessage());
        }//fin catch
        finally {
            try {
                con.close();
            }catch(Exception e) {
                System.out.println("Ocurrió un error al cerrar la conexión: " + e.getMessage());
            }//fin catch
        }//fin finally
        return false;
    }//fin metodo agregar Estudiante

    //Metodo para modificar estudiante
    public boolean modificarEstudiante(Estudiante estudiante){
        PreparedStatement ps;
        Connection con = getConnection();
        String sql = "UPDATE estudiantes2026 SET nombre=?, apellido=?, telefono=?, email=? WHERE idestudiantes2026=?";
        try{
            ps= con.prepareStatement(sql);
            ps.setString(1,estudiante.getNombre());
            ps.setString(2,estudiante.getApellido());
            ps.setString(3,estudiante.getTelefono());
            ps.setString(4,estudiante.getEmail());
            ps.setInt(5,estudiante.getIdEstudiante());
            ps.execute();
            return true;
        }catch (Exception e){
            System.out.println("Error al modificar estudiante: "+e.getMessage());
        }//Fin Catch
        finally {
            try {
                con.close();
            }catch (Exception e){
                System.out.println("Ocurrió un error al cerrar la conexión: "+e.getMessage());
            }// fin catc
        }//fin finally
        return false;
    }// Fin metodo modificarEstudiante

    public boolean eliminarEstudiante(Estudiante estudiante){
        PreparedStatement ps;
        Connection con = getConnection();
        String sql = "DELETE FROM estudiantes2026 WHERE idestudiantes2026=?";
        try{
            ps = con.prepareStatement(sql);
            ps.setInt(1,estudiante.getIdEstudiante());
            ps.execute();
            return true;
        }catch (Exception e){
            System.out.println("Error al eliminar estudiante: "+e.getMessage());
        }finally {
            try{
                con.close();
            }catch (Exception e){
                System.out.println("Ocurrió un error al cerrar la conexión: "+e.getMessage());
            }//fin catch
        }//fin finally
        return false;
    }


    static void main() {
        var estudianteDao = new EstudianteDAO();

        //Modificar estudiante
        //var estudianteModificado = new Estudiante(1,"Juan Carlos","Juarez","2604800221","juancarlosjuarez@gmail.com");
        //var modificado = estudianteDao.modificarEstudiante(estudianteModificado);
        //if(modificado)
        //    System.out.println("Estudiante modificado: "+estudianteModificado);
        //else
        //    System.out.println("No se modificó el estudiante: "+estudianteModificado);


        // Agregar estudiante
        //var nuevoEstudiante = new Estudiante("Roberto","Yague","2604351458","robertoy@gmail.com");
        //var agregado = estudianteDao.agregarEstudiante(nuevoEstudiante);
        //if(agregado)
        //  System.out.println("Estudiante agregado: "+nuevoEstudiante);
        //else
        //    System.out.println("No se pudo agregar el estudiante: "+nuevoEstudiante);

        //Eliminar estudiante con ID 3
        var estudianteEliminar= new Estudiante(4);
        var eliminado = estudianteDao.eliminarEstudiante(estudianteEliminar);
        if (eliminado)
           System.out.println("Estudiante eliminado: "+estudianteEliminar);
        else
            System.out.println("No se eliminó el estudiante: "+estudianteEliminar);

        //listar los estudiantes

        System.out.println("Listado de estudiantes: ");
        List<Estudiante> estudiantes = estudianteDao.listarEstudiantes();
        estudiantes.forEach(System.out::println); //Funcion lambda para imprimir



        //Buscar por ID
        //var estudiante1 = new Estudiante(1);
        //System.out.println("Estudiantes antes de la busqueda: "+ estudiante1);
        //var encontrado = estudianteDao.buscarEstudiantePorId(estudiante1);
        //if(encontrado)
        //    System.out.println("Estudiante encontrado: "+estudiante1);
        //else
        //    System.out.println("No se encontró el estudiante: "+ estudiante1.getIdEstudiante());
    }
}
