/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package cnc_hotwire;

/**
 *
 * @author jesemil
 */
public class SerialPort {
    static String port;
    int baudeRate;

    public SerialPort(String port, int baudeRate) {
        this.port = port;
        this.baudeRate = baudeRate;
    }
    
    public static ProcessBuilder openSerialCommunication(){
        
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        // Construye el comando para ejecutar docker-compose
        ProcessBuilder serial_handler_process = new ProcessBuilder("docker-compose","exec","-T", "cnc-motor-control",
                 "python","serial_handler.py", port);
        serial_handler_process.redirectErrorStream(true);
        //serial_handler_process.redirectOutput();
        
        serial_handler_process.directory(new java.io.File(dockerComposeFile));      
        return serial_handler_process;        
    }
}
