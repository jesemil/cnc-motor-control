package interfazmcnc;
import gui.Principal;
import gui.Inicio;
import java.io.IOException;

public class InterfazMCNC {

    public static void main(String[] args) {
        // TODO code application logic here
        Inicio pantalla = new Inicio();
        pantalla.setVisible(true);
        //pantalla.setLocation(50, 100);
        //pantalla.setSize(102,600);
        
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        // Construye el comando para ejecutar docker-compose
        ProcessBuilder upDocker = new ProcessBuilder(
                "docker-compose", "up","-d");
        upDocker.directory(new java.io.File(dockerComposeFile));
        upDocker.redirectErrorStream(true);
        upDocker.inheritIO();
        
        try {
            Process upDockerProcess = upDocker.start();
            int exitCode = upDockerProcess.waitFor();
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        
    }
    
}
