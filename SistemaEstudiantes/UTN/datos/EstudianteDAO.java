package UTN.datos;

import UTN.dominio.Estudiante;
import static UTN.conexion.Conexion.getConnection;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

public class EstudianteDAO {
    // Metodo listar
    public List<Estudiante> listarEstudiantes() {
        List<Estudiante> estudiantes = new ArrayList<>();
        // Creamos los objetos para la comunicacion con la base de datos
        PreparedStatement ps; // Envia la sentencia a la base de datos
        ResultSet rs; // Obtenemos el resultado de la ejecucion de la setnecia
        // CReamos un obhjeto del tipò conexion
        Connection con = getConnection();
        String sql = "SELECT * FROM estudiantes ORDER BY idestudiantes";
        try {
            ps = con.prepareStatement(sql);
            rs = ps.executeQuery();
            while (rs.next()) {
                var estudiante = new Estudiante();
                estudiante.setIdEstudiante(rs.getInt("idestudiantes"));
                estudiante.setNombre(rs.getString("nombre"));
                estudiante.setApellido(rs.getString("apellido"));
                estudiante.setTelefono(rs.getString("telefono"));
                estudiante.setEmail(rs.getString("email"));
                // Agregamos a la lista
                estudiantes.add(estudiante);
            }
        } 
        catch (Exception e) {
            System.out.println("Ocurrio un error al sleccionar datos: " + e.getMessage());
        }
        finally {
            try {
                con.close();
            } catch (Exception e) {
                System.out.println("Ocurrio un error al cerrar la conexion" + e.getMessage());
            }
        }
        return estudiantes;
    } // Fin metodo Listar
    
    // 
    public boolean buscarEstudiantePorId(Estudiante estudiante) {
        PreparedStatement ps; 
        ResultSet rs; 
        // CReamos un obhjeto del tipò conexion
        Connection con = getConnection();
        String sql = "SELECT * FROM estudiantes WHERE idestudiantes = ?";
        try {
            ps = con.prepareStatement(sql);
            ps.setInt(1, estudiante.getIdEstudiante());
            rs = ps.executeQuery();
            if (rs.next()) {
                estudiante.setNombre(rs.getString("nombre"));
                estudiante.setApellido(rs.getString("apellido"));
                estudiante.setTelefono(rs.getString("telefono"));
                estudiante.setEmail(rs.getString("email"));
                return true;
            } // Find if
        } 
        catch (Exception e) {
            System.out.println("Ocurrio un error al buscar estudiante: " + e.getMessage());
        } // Fin catch
        finally {
            try {
                con.close();
            } 
            catch (Exception e) {
                System.out.println("Ocurrio un error al cerrar la conexion" + e.getMessage());
            } // Fin catch
        } // Fin finally
        return false;
    } // Fin metodo buscarEstudiantePorId

    // Merodo para agregar un estudiante
    public boolean agregarEstudiante(Estudiante estudiante) {
        PreparedStatement ps; 
        // CReamos un obhjeto del tipò conexion
        Connection con = getConnection();
        String sql = "INSERT INTO estudiantes (nombre, apellido, telefono, email) VALUES (?, ?, ?, ?)";
        try {
            ps = con.prepareStatement(sql);
            ps.setString(1, estudiante.getNombre());
            ps.setString(2, estudiante.getApellido());
            ps.setString(3, estudiante.getTelefono());
            ps.setString(4, estudiante.getEmail());
            ps.execute();
            return true;
        } 
        catch (Exception e) {
            System.out.println("Ocurrio un error al agregar el estudiante: " + e.getMessage());
        } // Fin catch
        finally {
            try {
                con.close();
            } 
            catch (Exception e) {
                System.out.println("Ocurrio un error al cerrar la conexion" + e.getMessage());
            } // Fin catch
        } // Fin finally
        return false;
    } // Fin metodo agregarEstudiante


    // Merodo para agregar un estudiante
    public boolean modificarEstudiante(Estudiante estudiante) {
        PreparedStatement ps; 
        // CReamos un obhjeto del tipò conexion
        Connection con = getConnection();
        String sql = "UPDATE estudiantes SET nombre = ?, apellido = ?, telefono = ?, email = ? WHERE idestudiantes = ?";
        try {
            ps = con.prepareStatement(sql);
            ps.setString(1, estudiante.getNombre());
            ps.setString(2, estudiante.getApellido());
            ps.setString(3, estudiante.getTelefono());
            ps.setString(4, estudiante.getEmail());
            ps.setInt(5, estudiante.getIdEstudiante());
            ps.execute();
            return true;
        } 
        catch (Exception e) {
            System.out.println("Ocurrio un error al modificar el estudiante: " + e.getMessage());
        } // Fin catch
        finally {
            try {
                con.close();
            } 
            catch (Exception e) {
                System.out.println("Ocurrio un error al cerrar la conexion" + e.getMessage());
            } // Fin catch
        } // Fin finally
        return false;
    } // Fin metodo agregarEstudiante

    // Merodo para agregar un estudiante
    public boolean eliminarEstudiante(Estudiante estudiante) {
        PreparedStatement ps; 
        // CReamos un obhjeto del tipò conexion
        Connection con = getConnection();
        String sql = "DELETE FROM estudiantes WHERE idestudiantes = ?";
        try {
            ps = con.prepareStatement(sql);
            ps.setInt(1, estudiante.getIdEstudiante());
            ps.execute();
            return true;
        } 
        catch (Exception e) {
            System.out.println("Ocurrio un error al eliminar el estudiante: " + e.getMessage());
        } // Fin catch
        finally {
            try {
                con.close();
            } 
            catch (Exception e) {
                System.out.println("Ocurrio un error al cerrar la conexion" + e.getMessage());
            } // Fin catch
        } // Fin finally
        return false;
    } // Fin metodo agregarEstudiante

    // -------------------------------------------------------------------------
/*
    public static void main(String[] args) {
        var estudianteDao = new EstudianteDAO();

        // Buscar estudiante por ID
        var estudiante1 = new Estudiante(1);
        System.out.println("Estudiante antes de la busqueda: " + estudiante1);
        var encontrado = estudianteDao.buscarEstudiantePorId(estudiante1);
        if (encontrado) {
            System.out.println("Estudiante encontrado: " + estudiante1);
        }
        else {
            System.out.println("No se encontro el estudiante: " + estudiante1.getIdEstudiante());
        }
         
        // Agregar un estudiante
        var nuevoEstudiante = new Estudiante("Carlos", "Lara", "123456789", "clara@mail.com");
        var agregado = estudianteDao.agregarEstudiante(nuevoEstudiante);
        if (agregado) {
            System.out.println("Estudiante agregado: " + nuevoEstudiante);
        }
        else {
            System.out.println("No se agrego el estudiante: " + nuevoEstudiante);
        }
    
        // Modificar un estudiante
        var estudianteModificado = new Estudiante(4, "Juan Carlos", "Juarez", "123456789", "jjuarez@mail.com");
        var modificado = estudianteDao.modificarEstudiante(estudianteModificado);
        if (modificado) {
            System.out.println("Estudiante modificado: " + estudianteModificado);
        }
        else {
            System.out.println("No se modifico el estudiante: " + nuevoEstudiante);
        }
        
        // Eliminarun estudiante
        var estudianteEliminado = new Estudiante(5);
        var eliminado = estudianteDao.eliminarEstudiante(estudianteEliminado);
        if (eliminado) {
            System.out.println("Estudiante eliminado: " + estudianteEliminado);
        }
        else {
            System.out.println("No se elimino el estudiante: " + estudianteEliminado);
        }

        // Listar los estudiantes
        System.out.println("Listado de estudiantes: ");
        List<Estudiante>  estudiantes = estudianteDao.listarEstudiantes();
        estudiantes.forEach(System.out::println); // Funcion lambda para imprimir
    }
*/
}
