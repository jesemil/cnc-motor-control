/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package cnc_hotwire;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.io.OutputStream;
import javax.swing.SwingUtilities;
/**
 *
 * @author jesemil
 */
public class MovimientoMotor {
    static int speed; //Wire speed
    static String gcode_route; //Route where gcode file is
    static String serial_route; //Serial port
    static int max_x; //EPS X block size
    static int max_y; //EPS Y block size
    static String homing_mode;
    String status; //grbl status idle,
    
    public MovimientoMotor (int speed, int max_x, int max_y, String homing_mode){
        this.speed = speed;
        this.max_x = max_x;
        this.max_y = max_y;
        this.homing_mode = homing_mode;
    }
    
    public MovimientoMotor (){
    }


    public int getSpeed() {
        return speed;
    }

    public String getGcode_route() {
        return gcode_route;
    }

    public int getMax_x() {
        return max_x;
    }

    public int getMax_y() {
        return max_y;
    }

    public String getStatus() {
        return status;
    }

    public static String getHoming_mode() {
        return homing_mode;
    }
    
    public void setSpeed(int speed) {
        this.speed = speed;
    }

    public void setGcode_route(String gcode_route) {
        this.gcode_route = gcode_route;
    }

    public void setMax_x(int max_x) {
        this.max_x = max_x;
    }

    public void setMax_y(int max_y) {
        this.max_y = max_y;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public static void setSerial_route(String serial_route) {
        MovimientoMotor.serial_route = serial_route;
    }

    public static void setHoming_mode(String homing_mode) {
        MovimientoMotor.homing_mode = homing_mode;
    }
        
    public static String findPort(){
        String prefix = "/dev/";
        ProcessBuilder processBuilder = new ProcessBuilder("ls", prefix);
//        processBuilder.redirectErrorStream(true);

        try {
            Process process = processBuilder.start();
            InputStream inputStream = process.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));

            String line;
            while ((line = reader.readLine()) != null) {
                if (line.contains("ACM")) {
                    return prefix+line;
                }
            }

            process.waitFor(); // Wait for the process to finish
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }

        return null;
    }
    
    public static ProcessBuilder grblStreaming(){
        
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        // Construye el comando para ejecutar docker-compose
        ProcessBuilder python_streaming_process = new ProcessBuilder("docker-compose","exec","-T", "cnc-motor-control",
                 "python","grbl_streaming.py",gcode_route ,serial_route);
        python_streaming_process.directory(new java.io.File(dockerComposeFile));      
        return python_streaming_process;        
    }
    
    public static void moveMotors (String dir){
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        // Construye el comando para ejecutar docker-compose
        ProcessBuilder moveMotors_process = new ProcessBuilder(
                "docker-compose","exec","-T", "cnc-motor-control","python", "/app/commands_stream.py",serial_route,"-m", "-mm", dir);
        
        moveMotors_process.directory(new java.io.File(dockerComposeFile));
        moveMotors_process.redirectErrorStream(true);
        moveMotors_process.inheritIO();
        Thread processThread = new Thread(() -> {
        try{    
            Process python_streaming = moveMotors_process.start();
            // Espera a que el proceso termine
            int exitCode = python_streaming.waitFor();
            
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        });
        processThread.start();
    }
    
    public static Boolean setSettingsGrbl (){
        boolean error= false;
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        // Construye el comando para ejecutar docker-compose
         ProcessBuilder setSettingsGrbl_process = new ProcessBuilder(
                "docker-compose","exec","-T", "cnc-motor-control","python","/app/commands_stream.py", serial_route, "-u","--speed",
                Integer.toString(speed), "--homing_mode", homing_mode, "--block_x", 
                        Integer.toString(max_x), "--block_y", Integer.toString(max_y));
        
        setSettingsGrbl_process.directory(new java.io.File(dockerComposeFile));
        setSettingsGrbl_process.redirectErrorStream(true);
        setSettingsGrbl_process.redirectOutput();
        try {
            Process getStatusGrbl = setSettingsGrbl_process.start();
            InputStream dockerInputStream = getStatusGrbl.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(dockerInputStream));                     
            try {
                String lines = null;
                while((lines=reader.readLine())!=null){
                    System.out.println(lines);
                    if(lines.contains("error")){
                        error = true;
                    }
                }
            }catch (IOException e) {
                e.printStackTrace();
            }finally {
                try {
                    // Cierra el buffer y el InputStream al salir del hilo
                    reader.close();
                    dockerInputStream.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            int pruneExitCode = getStatusGrbl.waitFor(); // Espera a que el proceso de prune termine
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            return true;
        }
        return error;
    }
    
    public static ProcessBuilder grblHoming (){
        
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        // Construye el comando para ejecutar docker-compose
        ProcessBuilder homingGrbl_process = new ProcessBuilder(
                "docker-compose","exec","-T", "cnc-motor-control","python","/app/commands_stream.py", serial_route, "-hm");
        
        homingGrbl_process.directory(new java.io.File(dockerComposeFile));
        return homingGrbl_process;
    }
    
    public void grblReset (){
        
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        // Construye el comando para ejecutar docker-compose
        ProcessBuilder resetGrbl_process = new ProcessBuilder(
                "docker-compose","exec","-T", "cnc-motor-control","python","/app/commands_stream.py", serial_route, "-rs");
        
        resetGrbl_process.directory(new java.io.File(dockerComposeFile));
        resetGrbl_process.redirectErrorStream(true);
        Thread processThread = new Thread(() -> {
        try {
            //Process process_prune = processBuilderPrune.start();
            //int pruneExitCode = process_prune.waitFor(); // Espera a que el proceso de prune termine
            Process grblReset = resetGrbl_process.start();
            InputStream dockerInputStream = grblReset.getInputStream();
                        BufferedReader reader = new BufferedReader(new InputStreamReader(dockerInputStream),1);

                        String lines = null;
                        boolean alarm;
                        while((lines=reader.readLine())!=null){
                            final String finalLines = lines; // Variable final para ser utilizada en la expresión lambda
                            SwingUtilities.invokeLater(() -> {
                                System.out.println(finalLines);
                            });
                        }
            
            int exitCode = grblReset.waitFor();
            System.out.print("termino el reinicio");
            
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        });
        // Inicia el hilo de lectura
        processThread.start();
    }
    
        
    public static String [] getGrblStatus (){
        
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        System.out.println(dockerComposeFile);
        // Construye el comando para ejecutar docker-compose
        //ProcessBuilder processBuilderPrune = new ProcessBuilder("docker", "container", "prune", "-f");
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        ProcessBuilder getStatusGrbl_process = new ProcessBuilder(
                "docker-compose", "exec","-T", "cnc-motor-control","python","/app/commands_stream.py",serial_route,"-s");
        
        //processBuilderPrune.directory(new java.io.File(dockerComposeFile));
        getStatusGrbl_process.directory(new java.io.File(dockerComposeFile));
        getStatusGrbl_process.redirectErrorStream(true);
        try {
            //Process process_prune = processBuilderPrune.start();
            //int pruneExitCode = process_prune.waitFor(); // Espera a que el proceso de prune termine
            Process getStatusGrbl = getStatusGrbl_process.start();
            InputStream dockerInputStream = getStatusGrbl.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(dockerInputStream));
            final String[] datos = new String[3];
            
            Thread readerThread = new Thread(() -> {
                try {
                    String lines = null;
                    while((lines=reader.readLine())!=null){
                        System.out.println(lines);
                        if(lines.contains("<")){
                            Pattern pattern = Pattern.compile("<([^|]+)\\|MPos:(-?\\d+\\.\\d+),(-?\\d+\\.\\d+),(-?\\d+\\.\\d+)");
                            Matcher matcher = pattern.matcher(lines);
                            if (matcher.find()) {
                                // Obtener MPos y status
                                datos[0] = matcher.group(1);
                                datos[1] = matcher.group(2);
                                datos[2] = matcher.group(3);
                            }
                        }
                    }
                }catch (IOException e) {
                        e.printStackTrace();
                }finally {
                    try {
                        // Cierra el buffer y el InputStream al salir del hilo
                        reader.close();
                        dockerInputStream.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            });

            // Inicia el hilo de lectura
            readerThread.start();
            int exitCode = getStatusGrbl.waitFor();
            
            return datos;
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            return null;
        }
    }
    
    public static void grblHold (){
        
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        // Construye el comando para ejecutar docker-compose
        //ProcessBuilder processBuilderPrune = new ProcessBuilder("docker", "container", "prune", "-f");

        ProcessBuilder grblHold_process = new ProcessBuilder(
                "docker-compose", "exec","-T", "cnc-motor-control","python","/app/commands_stream.py",serial_route,"-x");
        
        //processBuilderPrune.directory(new java.io.File(dockerComposeFile));
        grblHold_process.directory(new java.io.File(dockerComposeFile));
        grblHold_process.redirectErrorStream(true);
        Thread processThread = new Thread(() -> {
        try {
            //Process process_prune = processBuilderPrune.start();
            //int pruneExitCode = process_prune.waitFor(); // Espera a que el proceso de prune termine
            Process grblHold = grblHold_process.start();
            int exitCode = grblHold.waitFor();
            
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        });
        // Inicia el hilo de lectura
        processThread.start();
    }
    
    public static void grblResume (){
        
        String dockerComposeFile = System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        if (dockerComposeFile.contains("dist")){
            dockerComposeFile = dockerComposeFile.replace("/dist","");
        }
        // Construye el comando para ejecutar docker-compose
        //ProcessBuilder processBuilderPrune = new ProcessBuilder("docker", "container", "prune", "-f");

        ProcessBuilder grblResume_process = new ProcessBuilder(
                "docker-compose", "exec","-T", "cnc-motor-control","python","/app/commands_stream.py",serial_route,"-r");
        
        //processBuilderPrune.directory(new java.io.File(dockerComposeFile));
        grblResume_process.directory(new java.io.File(dockerComposeFile));
        grblResume_process.redirectErrorStream(true);
        Thread processThread = new Thread(() -> {
        try {
            //Process process_prune = processBuilderPrune.start();
            //int pruneExitCode = process_prune.waitFor(); // Espera a que el proceso de prune termine
            Process grblResume = grblResume_process.start();
            int exitCode = grblResume.waitFor();
            
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        });
        // Inicia el hilo de lectura
        processThread.start();
    }
    
    public static void main(String[] args) {
        serial_route=findPort();
        gcode_route=System.getProperty("user.dir").replace("/InterfazMCNC","/python_scripts");
        if (gcode_route.contains("dist")){
            gcode_route = gcode_route.replace("/dist","");
        }
        String datos[] = getGrblStatus();
        
        System.out.print(datos[0]+datos[1]+datos[2]);
        /*
        System.out.println(gcode_route);
        ProcessBuilder grblStreaming = grblStreaming();
        try{    
            Process python_streaming = grblStreaming.start();
            InputStream dockerInputStream = python_streaming.getInputStream();
            System.out.println("Iniciando proceso");
            BufferedReader reader = new BufferedReader(new InputStreamReader(dockerInputStream),1);
            Thread readerThread = new Thread(() -> {
                try {
                    String lines = null;
                    System.out.print(reader.readLine());
                    while((lines=reader.readLine())!=null){
                        if(lines.contains("MSG:")){
                            Pattern pattern = Pattern.compile("MPos:(-?\\d+\\.\\d+),(-?\\d+\\.\\d+),");
                            Matcher matcher = pattern.matcher(lines);
                            if (matcher.find()) {
                                // Obtener los dos primeros números MPos
                                String mpos1 = matcher.group(1);
                                String mpos2 = matcher.group(2);

                                // Imprimir los resultados
                                System.out.println("X: " + mpos1 + ", Y: " + mpos2);
                            } 
                            else {
                                System.out.println("No se encontraron números MPos en la cadena.");
                            }
                        }
                        else{
                            System.out.println("lines: "+lines);
                        }

                    }
                }catch (IOException e) {
                        e.printStackTrace();
                }
            });

            // Inicia el hilo de lectura
            readerThread.start();


            // Espera a que el proceso termine
            int exitCode = python_streaming.waitFor();

            // Imprime el código de salida del proceso
            //System.out.println("Código de salida: " + exitCode);
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        */
    }
}
