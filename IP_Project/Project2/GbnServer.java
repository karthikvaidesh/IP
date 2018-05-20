import java.io.*;
import java.net.*;
import java.util.*;

public class GbnServer extends Thread {
    
    private int port, ack = -1;
    private String transferFile;
    private double probability;
    private volatile boolean hasReceived;
    private DatagramSocket datagramSocket = null;

    public GbnServer(int port, String transferFile, double probability) throws SocketException {
        this.port = port;
        this.transferFile = transferFile;
        this.probability = probability;
        datagramSocket = new DatagramSocket(this.port);
        hasReceived = true;
        
    }

    public void run() {
        BufferedOutputStream buff = null;
        try {
        	int packetsLost = 0;
            System.out.println("GbnServer running at " + InetAddress.getLocalHost().getHostAddress()
            		+ " on port " + datagramSocket.getLocalPort());
            File file = new File(transferFile);
        	FileOutputStream fos = new FileOutputStream(file);
            buff = new BufferedOutputStream(fos);
           
			int packetType = 21845; //0101010101010101  => data packet
			while (hasReceived) {
    		    byte dataBuf[] = new byte[1024 * 1000 * 2];
    		    int buffLen = dataBuf.length;
    		    DatagramPacket datagrampacket = new DatagramPacket(dataBuf, buffLen);
    		    datagramSocket.receive(datagrampacket);
    		    ByteArrayInputStream baostream = new ByteArrayInputStream(datagrampacket.getData());
    		    ObjectInputStream outputStream = new ObjectInputStream(baostream);
    		    Packet Packet = (Packet) outputStream.readObject();
    		    if(Packet == null){
    		        buff.close();
    		        System.out.println("Packets Lost = " + packetsLost);
    		        datagramSocket.close();
    		        break;
			    }

			    Random random = new Random();
			    int randomNum = random.nextInt(100);
			    double randomProbability = (double)randomNum/100;
				int checkSum = 0;
				if (Packet.data !=null) {

					int i = 0;
                    while(i < Packet.data.length){    
				    	checkSum = ((i % 2) == 0) ? (checkSum + ((Packet.data[i] << 8) & 0xFF00)) 
				    			: (checkSum + ((Packet.data[i]) & 0xFF));

				    	if((Packet.data.length % 2) != 0){
				    		checkSum = checkSum + 0xFF;
				    	}

				        while ((checkSum >> 16) == 1){
				        	 checkSum =  ((checkSum & 0xFFFF) + (checkSum >> 16));
				             checkSum =  ~checkSum;
				        }
                        i++;
					} 
				}
			    int seqNum = Packet.sequencenumber;
			    
			    if(seqNum != ack) {

					if(probability < randomProbability) {
						if (Packet.type == packetType) {			
							if(Packet.checksum == checkSum) {
								ack++;
								buff.write(Packet.data);
								buff.flush();
								sendAck(seqNum, datagrampacket);
					         }
						}
					}
					else {
						System.out.printf("Packet loss, sequence number = %d \n", seqNum);
						packetsLost++;
					}
	
			    } else {
			    	sendAck(seqNum, datagrampacket);
			    }
			}
	
         
        } catch (Exception e) {
        	System.out.println("Error");
            hasReceived = false;
        }
    }
    
    private void sendAck(int seqNum, DatagramPacket datagrampacket) throws IOException {
    	short chkSum = 0;
        short ackType = (short)43690;    //1010101010101010, indicating that this is an ACK packet.
        byte ackData[] = null;
    	Packet ack = new Packet(seqNum, chkSum, ackType, ackData);
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream outStream = new ObjectOutputStream(baos);
        outStream.writeObject(ack);
        byte[] ackedData = baos.toByteArray();
        int ackDataLen = ackedData.length;
        DatagramPacket ackPacket = new DatagramPacket(ackedData, ackDataLen,
                                   datagrampacket.getAddress(), datagrampacket.getPort());
        datagramSocket.send(ackPacket);
    }

   
    
    public static void main(String[] args) throws SocketException {
        if (args.length != 3) {
            System.out.println("Please provide correct number of arguments");
                return;
        }
        new GbnServer(Integer.parseInt(args[0]), args[1], Double.parseDouble(args[2])).start();
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