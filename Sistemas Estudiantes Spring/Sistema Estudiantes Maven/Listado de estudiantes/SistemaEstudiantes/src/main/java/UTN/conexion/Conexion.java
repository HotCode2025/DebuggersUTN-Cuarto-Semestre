package UTN.conexion;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class Conexion {
    public static Connection getConnection(){
        Connection conexion = null;
        //variables para conectarnos a la base de datos
        var baseDatos = "estudiantes";
        var url = "jdbc:mysql://localhost:3306/"+baseDatos;
        var usuario = "root";
        var password = "enzo1234!";

        //cargamos la clase del driver de MySQL en memoria
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            conexion = DriverManager.getConnection(url, usuario, password);
        }catch(ClassNotFoundException | SQLException e){
            System.out.println("Ocurrió un error en la conexion: "+e.getMessage());
        }// Fin catch
        return conexion;
    }//fin metodo Connection
}
