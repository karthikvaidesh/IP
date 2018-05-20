import static java.net.InetAddress.getByName;
import java.io.*;
import java.net.*;
import java.util.*;


public class GbnClient extends Thread{
    private int transmitted  = -1, timeout = 1000, serverPort, windowSize, Mss, noOfPackets, lastPacket;
    private volatile int ack  = -1;
    private String server, fileToBeTransferred;
    private DatagramSocket dgramSoc = null;
    private final Packet buff[];

    public GbnClient(String server, int serverPort, String fileToBeTransferred, int WindowSize,
    			int MSS) throws SocketException, UnknownHostException {
    	this.server = server;
    	this.serverPort = serverPort;
    	this.fileToBeTransferred = fileToBeTransferred;
    	this.windowSize = WindowSize;
    	this.Mss = MSS;
    	int port = new Random().nextInt(6500) + 1000;	
    	dgramSoc = new DatagramSocket(port);
    	dgramSoc.connect(getByName(server), serverPort);
    	buff = new Packet[this.windowSize];
    	System.out.println("Client running at " + InetAddress.getLocalHost().getHostAddress()
    			+ " on port number " + dgramSoc.getLocalPort());
    }

    private class RemainingPackets extends Thread{
        private final DatagramSocket socDgram;
        private volatile boolean transfer;
        private boolean conn;
        public RemainingPackets(DatagramSocket dataSoc) {
            this.socDgram = dataSoc;
            transfer = true;
        }

        public void finish(){
            transfer = false;
        }

        public void run(){   //thread for remaining packets
            while(transfer){
            	int isSockOpen;
                byte buffData[] = new byte[1024 * 1000 * 2];
                int length = buffData.length;
                DatagramPacket dgramPac = new DatagramPacket(buffData, length);

                try {
                	conn = socDgram.isClosed();
                    if(conn)
                    	isSockOpen = 0;
                    else
                    	isSockOpen = 1;
                    if(isSockOpen == 1) {
                    	socDgram.receive(dgramPac);
                        ObjectInputStream outputStream = new ObjectInputStream(new ByteArrayInputStream(dgramPac.getData()));
                        Packet packet = (Packet) outputStream.readObject();
                        if (packet.type == (short)43690)
                        	ack = packet.sequencenumber;
                    }
                } catch (Exception e) {
                   
                }
            }
        }
    }



    public void run(){
        try{
        	boolean isThread = true;
        	if(isThread) {
                long startTime = System.currentTimeMillis();
	            File file = new File(fileToBeTransferred);
	            if(file.exists()){
                        int size = (int)file.length();
                        noOfPackets = size/Mss;                 //calculating the number of packets from the given file size
                        lastPacket = size % Mss;
                        byte data[] = new byte[Mss];
                        RemainingPackets newpkt = null;
                    
                        int lostPktCnt = 0;
                        int isNext = 1;
                        FileInputStream fis = new FileInputStream(file);
                        while(fis.read(data) >=0){
                             boolean success;
                            while(transmitted - ack == windowSize) {    //
                                if(System.currentTimeMillis() - buff[(ack+1) % windowSize].sentTime <= timeout){
                                    success = true;   //within RTO
                                }
                                else {
                                    success = false;  //timeout
                                }
                                if(!success) {
                                    int tempAck = ack;
                                    int i = 0;
                                    while(i < (transmitted - ack)) {
                                        System.out.println("Timeout, sequence number = " + buff[(tempAck + 1 + i) % windowSize].sequencenumber);
                                        lostPktCnt++;
                                        sendPacket(buff[(tempAck+1+i) % windowSize]);  //go back N packets
                                        i++;
                                    }
                                }
                            }       

                            byte byteToBeTransferred[] = new byte[Mss];
                            short dataType = (short)21845;      //0101010101010101, indicating that this is a data packet.
                            byte lastData[] = new byte[lastPacket];
                            byteToBeTransferred = data;
                            transmitted++;
                            if(transmitted == noOfPackets) {
                                for(int k = 0 ; k < lastPacket ; k++){
                                    lastData[k] = byteToBeTransferred[k];
                                }
                                byteToBeTransferred = lastData;
                            }
                            
                            int checksum = 0;
                            if (byteToBeTransferred != null){ 
                                int i=0;
                                while(i < byteToBeTransferred.length){
                                    if(i%2==0)
                                        checksum =checksum + ((byteToBeTransferred[i] << 8) & 0xFF00);
                                    else
                                        checksum =checksum + ((byteToBeTransferred[i]) & 0xFF);
                                    

                                    if((byteToBeTransferred.length % 2) != 0){
                                        checksum = checksum + 0xFF;
                                    }
                        
                                    while ((checksum >> 16) == 1){
                                         checksum =  ((checksum & 0xFFFF) + (checksum >> 16));
                                         checksum =  ~checksum;
                                    }
                                    i++;
                                }
                            }
                                
                            else{
                                checksum=0;
                            } 
                            Packet packet = new Packet(transmitted, checksum, dataType, byteToBeTransferred);
                            int index = (transmitted % windowSize);
                            buff[index] = packet;
                            sendPacket(packet) ;
                    
                            if(isNext == 1){
                                isNext = 0;
                                newpkt = new RemainingPackets(dgramSoc);
                                newpkt.start();
                            }
                            //GBN Logic
                            int tempAcked = ack; 
                            boolean flag = false;
                            while(tempAcked != transmitted) {
                                if(System.currentTimeMillis() - buff[(tempAcked+1) % windowSize].sentTime > timeout){
                                    flag = false;
                                }
                                else {
                                    flag = true;
                                }
                                if(!flag) {
                                    int j = 0;
                                    while(j < (transmitted - tempAcked)) { 
                                        System.out.println("Timeout, sequence number = " + buff[(tempAcked + 1 + j) % windowSize].sequencenumber);
                                        lostPktCnt++;
                                        sendPacket(buff[(tempAcked + 1 + j) % windowSize]);
                                        j++;
                                    }
                                }
                                tempAcked = ack;
                            }


                        }
                        fis.close();
                        long endTime = System.currentTimeMillis();  
                        sendPacket(null);
                        newpkt.finish();
                        isThread = false;
                        dgramSoc.close();
                        System.out.println("Delay: " + (endTime -startTime ));
                        //System.out.println("Packets Lost: " + lostPktCnt);              
                        dgramSoc.close();
	            	
	            } else{
	            	System.out.println("Error: 404 File Not Found !!"); 
	            }
        	}
        } catch (Exception e) {
           System.out.println("Server not reachable!!");
        }
    }

    private void sendPacket(Packet packet) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream outStream = new ObjectOutputStream(baos);
        outStream.writeObject(packet);
        byte[] sendData = baos.toByteArray();
        DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length,
        		getByName(server), serverPort);
        if(packet != null){
        	packet.sentTime = System.currentTimeMillis();
        	}
        	
        dgramSoc.send(sendPacket);
    }

    public static void main(String[] args) throws InterruptedException {
    	if(args.length != 5 ) 
            {
                System.out.println("Please provide correct number of arguments");
                return;
            }
    	try{
    		new GbnClient(args[0], Integer.parseInt(args[1]), args[2], Integer.parseInt(args[3]), Integer.parseInt(args[4])).start();
    	} catch (Exception e) {
    		System.out.println("Server not reachable!!");
    	}
    }
}
 class Packet implements Serializable{
    public int sequencenumber;
    public int checksum;
    public short type;
    public byte data[];
    public long sentTime;

    public Packet(int sequencenumber, int checksum, short type, byte[] data) {
        this.sequencenumber = sequencenumber;
        this.checksum = checksum;
        this.type = type;
        this.data = data;
    }

    
}
