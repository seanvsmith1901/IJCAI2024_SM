import java.awt.*;
import java.util.*;
import java.awt.event.*;
import java.lang.*;
import java.io.*;
import java.net.*;
import javax.swing.*;
import java.math.*;
import java.text.*;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics;
import javax.swing.JComponent;
import javax.swing.JFrame;


import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

class theButton {
	int x, y, w, h;

	public theButton(int _x, int _y, int _w, int _h) {
		x = _x;
		y = _y;
		w = _w;
		h = _h;
	}

	public boolean onButton(int mx, int my) {
		//System.out.println(mx + ", " + my);
		if ((Math.abs(mx - x) <= (w / 2)) && (Math.abs((my-6) - y) <= (h / 2)))
			return true;
		
		return false;
	}
}

class Eventing {
	String what;
	double amount;

	public Eventing(String _what, double _amount) {
		what = _what;
		amount = _amount;
	}
}

class myCanvas extends JComponent {
	Point mousePunto;
	String popMsg;

	int screenX = 0, screenY = 0;
	boolean gameOver = false;
	int round = -1, oldRound = -1, numPlayers = 0, humanIndex = 0;

	int[][] tokens;
	double[][] influence, prevInfluence;
	double[][][] influenceHistory;
	double[][] popularities;
	int[] allocations;
	theButton[] minusButtons;
	theButton[] plusButtons;
	theButton submit;
	Color[] theColors;

	double[] visualTraits;

	int descriptionIdx = -1;
	double steal_coef = 1.6;
	double give_coef = 1.3;
	double keep_coef = 0.95;
	double alpha = 0.2;

	theButton[] descriptionButtons;
	boolean[] isExpanded = new boolean[5];

	double[][] amountStolen;
	int stealUpdate;

    public myCanvas(int _numPlayers) {
		numPlayers = _numPlayers;
		initAll();

        MyThread thread = new MyThread();
        thread.start();
    }

	public void initAll() {
		allocations = new int[numPlayers];
		for (int i = 0; i < numPlayers; i++)
			allocations[i] = 0;

		tokens = new int[numPlayers][numPlayers];
		influence = new double[numPlayers+1][numPlayers];
		prevInfluence = new double[numPlayers+1][numPlayers];
		influenceHistory = new double[100][numPlayers+1][numPlayers];
		popularities = new double[1000][numPlayers];
		allocations = new int[numPlayers];

		for (int i = 0; i < numPlayers; i++) {
			for (int j = 0; j < 1000; j++) {
				popularities[j][i] = 1.0;
			}
		}
		
		submit = new theButton(60, 108 + numPlayers*25, 100, 30);
		minusButtons = new theButton[numPlayers];
		plusButtons = new theButton[numPlayers];
		theColors = new Color[numPlayers];
		for (int i = 0; i < numPlayers; i++) {
			minusButtons[i] = new theButton(291, 91 + i*25, 20, 16);
			plusButtons[i] = new theButton(344, 91 + i*25, 20, 16);
		}

		if (numPlayers >= 1)
			theColors[0] = new Color(166, 206, 227);
		if (numPlayers >= 2)
			theColors[1] = new Color(31, 120, 180);
		if (numPlayers >= 3)
			theColors[2] = new Color(178, 223, 138);
		if (numPlayers >= 4)
			theColors[3] =  new Color(51, 160, 44);
		if (numPlayers >= 5)
			theColors[4] = new Color(251, 154, 153);
		if (numPlayers >= 6)
			theColors[5] = new Color(227, 26, 28);
		if (numPlayers >= 7)
			theColors[6] = new Color(253, 191, 111);
		if (numPlayers >= 8)
			theColors[7] = new Color(255, 127, 0);
		if (numPlayers >= 9)
			theColors[8] = new Color(202, 178, 214);
		if (numPlayers >= 10)
			theColors[9] = new Color(106, 61, 154);
		if (numPlayers >= 11)
			theColors[10] = new Color(141, 211, 199);
		if (numPlayers >= 12)
			theColors[11] = new Color(255, 255, 179);
		if (numPlayers >= 13)
			theColors[12] = new Color(190, 186, 218);
		if (numPlayers >= 14)
			theColors[13] = new Color(251, 128, 114);
		if (numPlayers >= 15)
			theColors[14] = new Color(228, 177, 211);
		if (numPlayers >= 16)
			theColors[15] = new Color(253, 180, 98);
		if (numPlayers >= 17)
			theColors[16] = new Color(179, 222, 105);
		if (numPlayers >= 18)
			theColors[17] = new Color(252, 205, 229);
		if (numPlayers >= 19)
			theColors[18] = new Color(217, 217, 217);
		if (numPlayers >= 20)
			theColors[19] = new Color(188, 128, 189);

		visualTraits = new double[numPlayers];

		descriptionButtons = new theButton[5];
		for (int i = 0; i < 5; i++) {
			isExpanded[i] = false;
			descriptionButtons[i] = new theButton(0,0,0,0);
		}

		amountStolen = new double[100][numPlayers];
		stealUpdate = 0;
		for (int i = 0; i < numPlayers; i++) {
			amountStolen[0][i] = 0.0;
		}
	}

	public void updateScreenPosition(int x, int y) {
		screenX = x;
		screenY = y;
		//System.out.println("Screen: " + screenX + ", " + screenY);
	}

	public void theClick(boolean isLeft, int x, int y) {
		for (int i = 0; i < numPlayers; i++) {
			if (i == humanIndex)
				continue;

			if (minusButtons[i].onButton(x, y)) {
				//System.out.println("minusButton: " + i);
				int count = 1;
				if (!isLeft)
					count = 5;
				
				for (int j = 0; j < count; j++) {
					if (allocations[i] > 0) {
						allocations[i] --;
						allocations[humanIndex] ++;
					}
					else {
						if (allocations[humanIndex] > 0) {
							allocations[i] --;
							allocations[humanIndex] --;
						}
					}
				}
				repaint();
			}
			if (plusButtons[i].onButton(x, y)) {
				//System.out.println("plusButton: " + i);
				int count = 1;
				if (!isLeft)
					count = 5;
				
				for (int j = 0; j < count; j++) {
					if (allocations[i] < 0) {
						allocations[i] ++;
						allocations[humanIndex] ++;
					}
					else {
						if (allocations[humanIndex] > 0) {
							allocations[i] ++;
							allocations[humanIndex] --;
						}
					}
				}
				repaint();
			}
		}

		if (submit.onButton(x, y)) {
			// System.out.println("Submit!");
			try {
				String fnombre = "../State/HumanAllocations.tmp";
				BufferedWriter writer = new BufferedWriter(new FileWriter(fnombre));		

				writer.write("" + round + "\n");
				for (int i = 0; i < numPlayers; i++) {
					writer.write("" + allocations[i] + "\n");
				}

				writer.close();

				Runtime rt = Runtime.getRuntime();
		        if (System.getProperty("os.name") == "Windows") {
		            // this needs to get fixed due to the differences in move and mv in windows and linux. lets just make sure this complies first.
		            String mandato = "move ../State/HumanAllocations.tmp ../State/HumanAllocations.txt";
				    Process pr = rt.exec(mandato);
		        }
		        else {
		            String mandato = "move ../State/HumanAllocations.tmp ../State/HumanAllocations.txt";
				    Process pr = rt.exec(mandato);
		        }

			}
			catch (IOException e) {
				System.out.println(e);
			}		

		}

		// see if popularity description is selected
		for (int i = 0; i < numPlayers; i++) {
			int targy = 95 + i * 25;
			int targx = 35;
			int h = 10, w = 18;
			if ((Math.abs(y - targy) < h) && (Math.abs(x - targx) < w))
				descriptionIdx = i;
		}

		// see if expanded description is selected
		for (int i = 0; i < 5; i++) {
			if (descriptionButtons[i].onButton(x, y)) {
				isExpanded[i] = !isExpanded[i];
			}
		}
	}

    public class MyThread extends Thread {

        public void run() {
            try {
                // repeatedly read status.txt and display
				while (true) {
					updateThings();
                    repaint();
                    Thread.sleep(200);
                }
            }
            catch (InterruptedException e) {
                System.out.println(e);
            }
        }

		public void updateThings() {
			try {
				String file = "../State/state.txt";
				BufferedReader reader = new BufferedReader(new FileReader(file));
				String str;

				// get game info
				str = reader.readLine();
				if (str.equals("fin"))
					gameOver = true;
				else
					gameOver = false;

				int tmpNumPlayers = Integer.parseInt(reader.readLine());
				if (tmpNumPlayers != numPlayers) {
					System.out.println("numPlayers problem");
					System.exit(1);
				}
				humanIndex = Integer.parseInt(reader.readLine());
				//System.out.println(humanIndex);
				//humanIndex = 2;
				round = Integer.parseInt(reader.readLine());
				if (round != oldRound) {
					for (int i = 0; i < numPlayers; i++)
						allocations[i] = 0;
		
					if (humanIndex >= 0)
						// specify the number of tokens
						// allocations[humanIndex] = numPlayers;
						// allocations[humanIndex] = (int)(numPlayers / 2);
						allocations[humanIndex] = numPlayers * 2;

					oldRound = round;
				}

				for (int i = 0; i < numPlayers; i++) {
					str = reader.readLine();
					//System.out.println("String: " + str);
					StringTokenizer st = new StringTokenizer(str, " ");
					for (int j = 0; j < (round+1); j++) {
						//System.out.println(j);
						String elstring = st.nextToken();
						//System.out.println("(" + elstring + ")");
						if (elstring.length() > 0) {
							popularities[j][i] = Double.parseDouble(elstring);
						}
					}
				}

				// get tokens sent
				for (int i = 0; i < numPlayers; i++) {
					str = reader.readLine();

					StringTokenizer st = new StringTokenizer(str, " ");
					for (int j = 0; j < numPlayers; j++) {
						tokens[i][j] = Integer.parseInt(st.nextToken());
					}
				}

				for (int t = 0; t < round+1; t++) {
					for (int i = 0; i < numPlayers; i++) {
						str = reader.readLine();

						StringTokenizer st = new StringTokenizer(str, " ");
						for (int j = 0; j < numPlayers; j++) {
							influenceHistory[t][j][i] = Double.parseDouble(st.nextToken());
						}
						if (t > 0)
							influenceHistory[t][numPlayers][i] = popularities[0][i] * Math.pow(1.0-0.2, t);
						else
							influenceHistory[t][numPlayers][i] = popularities[0][i];
					}
				}

				// get influence
				for (int i = 0; i < numPlayers; i++) {
					// str = reader.readLine();

					// StringTokenizer st = new StringTokenizer(str, " ");
					// for (int j = 0; j < numPlayers; j++) {
					// 	influence[j][i] = Double.parseDouble(st.nextToken());
					// }
					// influence[numPlayers][i] = popularities[0][i] * Math.pow(1.0-0.2, round-1);
					for (int j = 0; j < numPlayers; j++) {
						influence[j][i] = influenceHistory[round][j][i];
					}
					influence[numPlayers][i] = popularities[0][i] * Math.pow(1.0-0.2, round); 
				}

				// get previous influence
				for (int i = 0; i < numPlayers; i++) {
					// str = reader.readLine();

					// StringTokenizer st = new StringTokenizer(str, " ");
					// for (int j = 0; j < numPlayers; j++) {
					// 	prevInfluence[j][i] = Double.parseDouble(st.nextToken());
					// }
					if (round >= 1) {
						for (int j = 0; j < numPlayers; j++) {
							if ((round-1) > 0)
								prevInfluence[j][i] = influenceHistory[round-1][j][i];
							else
								prevInfluence[j][i] = 0.0;
						}
						prevInfluence[numPlayers][i] = popularities[0][i] * Math.pow(1.0-0.2, round-1);
					}
					else {
						for (int j = 0; j < numPlayers; j++) {
							prevInfluence[j][i] = influenceHistory[round][j][i];
						}
						prevInfluence[numPlayers][i] = popularities[0][i] * Math.pow(1.0-0.2, 0);
					}
				}

				reader.close();

				String file2 = "../State/visualTraits.txt";
				BufferedReader reader2 = new BufferedReader(new FileReader(file2));
				String str2;

				for (int i = 0; i < numPlayers; i++) {
					str2 = reader2.readLine();
					visualTraits[i] = Double.parseDouble(str2);
				}

				reader2.close();

				if (round > stealUpdate) {
					updateSteals();
				}
				if (round < stealUpdate) {
					stealUpdate = round;
					updateSteals();
				}
			}
			catch (IOException e) {
				// System.out.println(e);
				// assume no visualTraits.txt file
				for (int i = 0; i < numPlayers; i++) {
					visualTraits[i] = 50.0;
				}
			}
		}
    }

	public void updateSteals() {
		double tally = 0.0;
		for (int i = 0; i < numPlayers; i++) {
			tally = 0.0;
			for (int t = 1; t < round+1; t++) {
				// amountStolen[i] *= (1.0 - alpha);
				for (int j = 0; j < numPlayers; j++) {
					if (i != j)
						tally += getMin(0.0, influenceHistory[t][i][j] - influenceHistory[t-1][i][j] * (1.0 - alpha));
				}
				amountStolen[t][i] = tally;
				tally *= (1.0 - alpha);
			}
		}
		// System.out.println("Stolen as of round " + round);
		// for (int i = 0; i < numPlayers; i++) {
		// 	System.out.print("" + amountStolen[round][i] + ", ");
		// }
		// System.out.println();
		stealUpdate = round;
	}

	public double getMin(double v1, double v2) {
		if (v1 < v2)
			return v1;

		return v2;
	}

    public void paint(Graphics g) {
		mousePunto = MouseInfo.getPointerInfo().getLocation();
		mousePunto.x = mousePunto.x - screenX;
		mousePunto.y = mousePunto.y - screenY;
		//System.out.println(mousePunto.x + ", " + mousePunto.y);
		popMsg = "";
	
        g.setColor(new Color(0, 0, 0));
        g.fillRect(0, 0, 800, 800);
		
		drawHeaders(g);

		double tornadoAmplification = 0;
		if (round > 0) {
			// determine max tornado amplitude
			double mx = 0, mxp, mxm;
			for (int i = 0; i < numPlayers; i++) {
				mxp = mxm = 0.0;
				for (int j = 0; j < numPlayers+1; j++) {
					if (influence[j][i] > 0)
						mxp += influence[j][i];
					else
						mxp -= influence[j][i];
				}
				if (mxp > mx)
					mx = mxp;
				if (mxm > mx)
					mx = mxm;
			}
			tornadoAmplification = 175.0 / mx;
		}

		for (int i = 0; i < numPlayers; i++) {
			drawPlayer(g, i, 83 + i*25, tornadoAmplification);
		}
		drawPopMsg(g);

		drawPopularityGraph(g);

		explainPopularityChange(g);
    }

	public void explainPopularityChange(Graphics g) {
		int explanationLine = 135 + numPlayers * 25;

		g.setColor(new Color(255, 255, 255));
		g.drawLine(10, explanationLine, 1180, explanationLine);

		int idx = descriptionIdx;//determineDescriptionTarget();

		if (idx >= 0) {
			g.setFont(new Font("Courier", Font.PLAIN, 14));

			if (round == 0) {
				String increaseStr = "Player " + idx + "'s initial popularity is " + (int)(popularities[round][idx]);
				g.drawString(increaseStr, 10, explanationLine+20);
			}
			else {
				// g.setFont(new Font("Courier", Font.PLAIN, 12));

				g.drawString("Category", 44, explanationLine + 46);
				g.drawString("Impact on Popularity", 555, explanationLine + 46);

				g.drawLine(40, explanationLine+30, 720, explanationLine+30);
				g.drawLine(40, explanationLine+52, 720, explanationLine+52);

				int numTokens = 0;
				for (int i = 0; i < numPlayers; i++)
					numTokens += Math.abs(tokens[humanIndex][i]);
				Vector<String> myStr;
				int ny;
				if (idx == humanIndex) {
					g.drawString("Your change in popularity in the last round was due to the following:", 101, explanationLine+20);

					Vector<Eventing> trade = getTrade_self(numTokens);
					ny = writeEventings(g, trade, explanationLine + 69, "Trade", isExpanded[0]);
					Vector<Eventing> attacksReceived = getAttacksReceived_self(numTokens);
					Vector<Eventing> attacksCarriedOut = getAttacksCarriedOut_self(numTokens);
					ny = writeEventings(g, attacksCarriedOut, ny, "Attacks executed", isExpanded[2]);
					ny = writeEventings(g, attacksReceived, ny, "Attacks suffered", isExpanded[1]);
					Vector<Eventing> tokensKept = getKeeping_self(numTokens);
					ny = writeEventings(g, tokensKept, ny, "Keeping", isExpanded[3]);

					double ttl = 0.0;
					for (int i = 0; i < trade.size(); i++)
						ttl += trade.get(i).amount;
					for (int i = 0; i < attacksReceived.size(); i++)
						ttl += attacksReceived.get(i).amount;
					for (int i = 0; i < attacksCarriedOut.size(); i++)
						ttl += attacksCarriedOut.get(i).amount;
					for (int i = 0; i < tokensKept.size(); i++)
						ttl += tokensKept.get(i).amount;

					Vector<Eventing> reputation = getReputation(numTokens, popularities[round][idx] - popularities[round-1][idx], ttl);
					ny = writeEventings(g, reputation, ny, "Reputation", isExpanded[4]);
				}
				else {
					g.drawString("" + idx + "'s change in popularity in the last round was due to the following:", 101, explanationLine+20);

					// first, determine attacks, keeping, and giving (reverse engineer token allocations of all players)
					int inferredTokens[][] = inferTokenAllocations(numTokens);

					// System.out.println("\n");
					// for (int i = 0; i < numPlayers; i++) {
					// 	for (int j = 0; j < numPlayers; j++) {
					// 		System.out.print("" + inferredTokens[i][j] + " ");
					// 	}
					// 	System.out.println("");
					// }

					Vector<Eventing> trade = getTrade_others(numTokens, idx, inferredTokens);
					ny = writeEventings(g, trade, explanationLine + 69, "Trade (estimated)", isExpanded[0]);
					Vector<Eventing> attacksCarriedOut = getAttacksCarriedOut_others(numTokens, idx, inferredTokens);
					ny = writeEventings(g, attacksCarriedOut, ny, "Attacks executed (estimated)", isExpanded[2]);
					Vector<Eventing> attacksReceived = getAttacksReceived_others(numTokens, idx, inferredTokens);
					ny = writeEventings(g, attacksReceived, ny, "Attacks suffered (estimated)", isExpanded[1]);
					Vector<Eventing> tokensKept = getKeeping_others(numTokens, idx, inferredTokens);
					ny = writeEventings(g, tokensKept, ny, "Keeping (estimated)", isExpanded[3]);

					double ttl = 0.0;
					for (int i = 0; i < trade.size(); i++)
						ttl += trade.get(i).amount;
					for (int i = 0; i < attacksReceived.size(); i++)
						ttl += attacksReceived.get(i).amount;
					for (int i = 0; i < attacksCarriedOut.size(); i++)
						ttl += attacksCarriedOut.get(i).amount;
					for (int i = 0; i < tokensKept.size(); i++)
						ttl += tokensKept.get(i).amount;

					Vector<Eventing> reputation = getReputation(numTokens, popularities[round][idx] - popularities[round-1][idx], ttl);
					ny = writeEventings(g, reputation, ny, "Reputation (estimated)", isExpanded[4]);
				}

				g.drawLine(40, ny-14, 720, ny-14);

				g.setFont(new Font("Courier", Font.PLAIN, 14));
				g.drawString("Total change in popularity", 50, ny+3);
				String strVal = "" + String.format("%1$,.1f", (popularities[round][idx] - popularities[round-1][idx]));
				g.drawString(strVal, 616 - (strVal.length()-3) * 8, ny+3);
			}
		}
	}

	public int[][] inferTokenAllocations(int numTokens) {
		int inferredTokens[][] = new int[numPlayers][numPlayers];
		
		for (int idx = 0; idx < numPlayers; idx++) {
			// giving
			double giveWorth = give_coef * popularities[round-1][idx] * (1.0 / numTokens) * alpha;
			double givenVal;
			for (int i = 0; i < numPlayers; i++) {
				if (i == idx)
					continue;

				if (influence[idx][i] > 0.0) {
					givenVal = influence[idx][i] - (prevInfluence[idx][i] * (1.0 - alpha));
					inferredTokens[idx][i] = (int)((givenVal / giveWorth) + 0.5);
				}
				else
					inferredTokens[i][idx] = 0;
			}

			// keeping
			double keepAmount = (influence[idx][idx] + amountStolen[round][idx]) - ((prevInfluence[idx][idx] + amountStolen[round-1][idx]) * (1.0 - alpha));
			double keepWorth = keep_coef * popularities[round-1][idx] * (1.0 / numTokens) * alpha;
			inferredTokens[idx][idx] = (int)((keepAmount / keepWorth) + 0.5);
			if (inferredTokens[idx][idx] < 0.0)
				inferredTokens[idx][idx] = 0;
		}

		// stealing
		for (int idx = 0; idx < numPlayers; idx++) {
			double stealWorth = steal_coef * popularities[round-1][idx] * (1.0 / numTokens) * alpha;
			double baseline = popularities[round-1][idx] * (1.0 / numTokens) * alpha;

			int tokensRemaining = numTokens;
			Set<Integer> mayHaveAttacked = new TreeSet<Integer>();
			for (int i = 0; i < numPlayers; i++) {
				tokensRemaining -= inferredTokens[idx][i];
				if (((influence[idx][i] + (1.0 * stealWorth)) < (prevInfluence[idx][i] * (1.0 - alpha))) && (idx != i)) {
					mayHaveAttacked.add(i);
				}
			}

			if (tokensRemaining > 0) {
				if (mayHaveAttacked.size() > 0) {
					double totalAttack = 0.0;
					double taken, profit;
					Iterator<Integer> itr = mayHaveAttacked.iterator();
					int current;
					while(itr.hasNext()){
						current = itr.next();
						totalAttack -= (influence[idx][current] - (prevInfluence[idx][current] * (1.0 - alpha)));
					}

					itr = mayHaveAttacked.iterator();
					while(itr.hasNext()){
						current = itr.next();
						// System.out.println("totalAttack: " + totalAttack);
						// System.out.println("this one: " + (influence[idx][current] - (prevInfluence[idx][current] * (1.0 - alpha))));
						// System.out.println("tokensRemaining: " + tokensRemaining);
						inferredTokens[idx][current] = -(int)((-tokensRemaining * ((influence[idx][current] - (prevInfluence[idx][current] * (1.0 - alpha))) / totalAttack)) + 0.5);
					}
				}					
			}
		}

		// over-ride with known true values
		for (int i = 0; i < numPlayers; i++) {
			inferredTokens[humanIndex][i] = tokens[humanIndex][i];
			inferredTokens[i][humanIndex] = tokens[i][humanIndex];
		}

		// handling shortfall
		for (int idx = 0; idx < numPlayers; idx++) {
			if (idx == humanIndex)
				continue;
				
			int ttl = 0;
			for (int i = 0; i < numPlayers; i++)
				ttl += Math.abs(inferredTokens[idx][i]);

			if (ttl < numTokens) {
				inferredTokens[idx][idx] += numTokens - ttl;
			}
		}

		return inferredTokens;
	}

	public int writeEventings(Graphics g, Vector<Eventing> v, int sy, String titulo, boolean expanded) {
		double ttl = 0.0;
		for (int i = 0; i < v.size(); i++) {
			if (v.get(i).amount != -99999)
				ttl += v.get(i).amount;
		}

		g.setFont(new Font("Courier", Font.PLAIN, 14));
		g.drawString(titulo, 60, sy);
		String strVal = "" + String.format("%1$,.1f", (ttl));
		g.drawString(strVal, 616 - (strVal.length()-3) * 8, sy);

		int descriptionType = getDescriptionIndex(titulo);

		descriptionButtons[descriptionType].x = 55;
		descriptionButtons[descriptionType].y = sy-5;
		descriptionButtons[descriptionType].w = 10;
		descriptionButtons[descriptionType].h = 10;

		int ny = sy + 20;
		if (expanded) {
			int [] X = {50, 58, 54, 50};
			int [] Y = {sy-8, sy-8, sy-2, sy-8};
			g.fillPolygon(X, Y, 4);

			g.setFont(new Font("Courier", Font.PLAIN, 12));

			if (v.size() > 0) {
				for (int i = 0; i < v.size(); i++) {
					g.drawString(v.get(i).what, 80, sy + 19 + (i * 19));
					if (v.get(i).amount != -99999) {
						String val = "" + String.format("%1$,.1f", (v.get(i).amount));
						g.drawString(val, 580 - (val.length()-3) * 7, sy + 19 + (i * 19));
					}
					ny += 19;
				}
			}
			else if (descriptionIdx == humanIndex) {
				if (titulo.equals("Trade"))
					g.drawString("You did not give or receive any tokens in the last round", 80, sy + 19);
				else if (titulo.equals("Attacks suffered"))
					g.drawString("You were not attacked in the last round", 80, sy + 19);
				else if (titulo.equals("Attacks executed"))
					g.drawString("You did not attack anyone in the last round", 80, sy + 19);
				else if (titulo.equals("Keeping"))
					g.drawString("You did not keep any tokens in the last round", 80, sy + 19);
				else if (titulo.equals("Reputation"))
					g.drawString("No reputational effects in the last round", 80, sy + 19);

				ny += 19;
			}
			else {
				if (titulo.equals("Trade (estimated)"))
					g.drawString("Appears to have not given or received any tokens in the last round", 80, sy + 19);
				else if (titulo.equals("Attacks executed (estimated)"))
					g.drawString("Appears to have not attacked anyone in the last round", 80, sy + 19);
				else if (titulo.equals("Attacks suffered (estimated)"))
					g.drawString("Appears to have not been attacked by anyone in the last round", 80, sy + 19);
				else if (titulo.equals("Keeping (estimated)"))
					g.drawString("Appears to have not kept any tokens in the last round", 80, sy + 19);
				else if (titulo.equals("Reputation (estimated)"))
					g.drawString("No reputational effects in the last round", 80, sy + 19);

				ny += 19;
			}
		}
		else {
			int [] X = {52, 52, 58, 52};
			int [] Y = {sy-9, sy-1, sy-5, sy-9};
			g.fillPolygon(X, Y, 4);
		}

		return ny + 2;
	}

	public int getDescriptionIndex(String titulo) {
		if (titulo.equals("Trade") || titulo.equals("Trade (estimated)"))
			return 0;
		else if (titulo.equals("Attacks suffered") || titulo.equals("Attacks suffered (estimated)"))
			return 1;
		else if (titulo.equals("Attacks executed") || titulo.equals("Attacks executed (estimated)"))
			return 2;
		else if (titulo.equals("Keeping") || titulo.equals("Keeping (estimated)"))
			return 3;
		else if (titulo.equals("Reputation") || titulo.equals("Reputation (estimated)"))
			return 4;

		return -1;
	}

	public Vector<Eventing> getTrade_self(int numTokens) {
		Vector<Eventing> v = new Vector<>();
		double got, lost;
		int rcvd, gve;
		for (int i = 0; i < numPlayers; i++) {
			if (i == humanIndex)
				continue;

			if ((tokens[i][humanIndex] > 0) || (tokens[humanIndex][i] > 0)) {
				if (tokens[i][humanIndex] > 0)
					rcvd = tokens[i][humanIndex];
				else
					rcvd = 0;

				got = give_coef * popularities[round-1][i] * (rcvd / ((double)numTokens)) * alpha;

				if (tokens[humanIndex][i] > 0)
					gve = tokens[humanIndex][i];
				else
					gve = 0;
				lost = popularities[round-1][humanIndex] * (gve / ((double)numTokens)) * alpha;

				v.add(new Eventing("with " + i + " (gave " + gve + "; received " + rcvd + ")", got - lost));
			}
		}

		return v;
	}

	public Vector<Eventing> getTrade_others(int numTokens, int idx, int[][] inferredTokens) {
		Vector<Eventing> v = new Vector<>();
		double got, lost;
		int rcvd, gve;
		for (int i = 0; i < numPlayers; i++) {
			if (i == idx)
				continue;

			if ((inferredTokens[i][idx] > 0) || (inferredTokens[idx][i] > 0)) {
				if (inferredTokens[i][idx] > 0)
					rcvd = inferredTokens[i][idx];
				else
					rcvd = 0;

				got = give_coef * popularities[round-1][i] * (rcvd / ((double)numTokens)) * alpha;

				if (inferredTokens[idx][i] > 0)
					gve = inferredTokens[idx][i];
				else
					gve = 0;
				lost = popularities[round-1][idx] * (gve / ((double)numTokens)) * alpha;

				v.add(new Eventing("with " + i + " (gave " + gve + "; received " + rcvd + ")", got - lost));
			}
		}

		return v;
		// Vector<Eventing> v = new Vector<>();
		// double giveWorth = give_coef * popularities[round-1][idx] * (1.0 / numTokens) * alpha;
		// double receiveWorth, giveLoss, receiveGain;
		// for (int i = 0; i < numPlayers; i++) {
		// 	if (i == idx)
		// 		continue;

		// 	receiveWorth = give_coef * popularities[round-1][i] * (1.0 / numTokens) * alpha;
		// 	if (influence[idx][i] > 0.0)
		// 		giveLoss = (influence[idx][i] - (prevInfluence[idx][i] * (1.0 - alpha))) / give_coef;
		// 	else
		// 		giveLoss = 0.0;
			
		// 	if (influence[i][idx] > 0.0)
		// 		receiveGain = influence[i][idx] - (prevInfluence[i][idx] * (1.0 - alpha));
		// 	else
		// 		receiveGain = 0.0;

		// 	if ((giveLoss > (0.5 * giveWorth)) || (receiveGain > (0.5 * receiveWorth))) {
		// 		v.add(new Eventing("with " + i, receiveGain - giveLoss));
		// 	}
		// }

		// return v;
	}

	public Vector<Eventing> getAttacksReceived_self(int numTokens) {
		Vector<Eventing> v = new Vector<>();
		double shouldaTaken, didTake, ratio;

		for (int i = 0; i < numPlayers; i++) {
			if (tokens[i][humanIndex] < 0) {
				shouldaTaken = steal_coef * popularities[round-1][i] * (tokens[i][humanIndex] / ((double)numTokens)) * alpha;
				if (popularities[round][humanIndex] <= 0.0)
					didTake = influence[i][humanIndex] - (prevInfluence[i][humanIndex] * (1.0 - alpha));
				else
					didTake = stealCoef(humanIndex) * popularities[round-1][i] * (tokens[i][humanIndex] / ((double)numTokens)) * alpha;
				ratio = didTake / shouldaTaken;
				// System.out.println("shouldaTaken: " + shouldaTaken);
				// System.out.println("didTake: " + didTake);

				if (ratio > ((steal_coef-0.1) / steal_coef))
					v.add(new Eventing("" + i + " attacked you with " + (-tokens[i][humanIndex]) + " tokens", didTake));
				else if (ratio > 0.1)
					v.add(new Eventing("" + i + " attacked you with " + (-tokens[i][humanIndex]) + " tokens (you partially blocked it)", didTake));
				else if (didTake < 0.0)
					v.add(new Eventing("" + i + " attacked you with " + (-tokens[i][humanIndex]) + " tokens (you blocked it)", didTake));
				else
					v.add(new Eventing("" + i + " attacked you with " + (-tokens[i][humanIndex]) + " tokens (you blocked it)", 0.0));
			}
		}

		return v;
	}

	public Vector<Eventing> getAttacksReceived_others(int numTokens, int idx, int[][] inferredTokens) {
		Vector<Eventing> v = new Vector<>();
		double shouldaTaken, didTake, ratio;

		for (int i = 0; i < numPlayers; i++) {
			if (inferredTokens[i][idx] < 0) {
				shouldaTaken = steal_coef * popularities[round-1][i] * (inferredTokens[i][idx] / ((double)numTokens)) * alpha;
				if (popularities[round][idx] <= 0.0)
					didTake = influence[i][idx] - (prevInfluence[i][idx] * (1.0 - alpha));
				else
					didTake = stealCoef(idx) * popularities[round-1][i] * (inferredTokens[i][idx] / ((double)numTokens)) * alpha;
				ratio = didTake / shouldaTaken;
				// System.out.println("shouldaTaken: " + shouldaTaken);
				// System.out.println("didTake: " + didTake);

				if (ratio > ((steal_coef-0.1) / steal_coef))
					v.add(new Eventing("attacked by " + i + " with " + (-inferredTokens[i][idx]) + " tokens", didTake));
				else if (ratio > 0.1)
					v.add(new Eventing("attacked by " + i + " with " + (-inferredTokens[i][idx]) + " tokens (" + idx + " partially blocked it)", didTake));
				else if (didTake < 0.0)
					v.add(new Eventing("attacked by " + i + " with " + (-inferredTokens[i][idx]) + " tokens (" + idx + " blocked it)", didTake));
				else
					v.add(new Eventing("attacked by " + i + " with " + (-inferredTokens[i][idx]) + " tokens (" + idx + " blocked it)", 0.0));
			}
		}

		return v;
	}

	public Vector<Eventing> getAttacksCarriedOut_self(int numTokens) {
		Vector<Eventing> v = new Vector<>();
		double shouldaTaken, didTake, baseline, ratio;

		for (int i = 0; i < numPlayers; i++) {
			if (tokens[humanIndex][i] < 0) {
				shouldaTaken = steal_coef * popularities[round-1][humanIndex] * (tokens[humanIndex][i] / ((double)numTokens)) * alpha;
				baseline = popularities[round-1][humanIndex] * (tokens[humanIndex][i] / ((double)numTokens)) * alpha;
				// if (popularities[round][i] <= 0.0)
				didTake = influence[humanIndex][i] - (prevInfluence[humanIndex][i] * (1.0 - alpha));
				// else
				// 	didTake = stealCoef(i) * popularities[round-1][humanIndex] * (tokens[humanIndex][i] / ((double)numTokens)) * alpha;
				ratio = didTake / shouldaTaken;
				if (ratio > ((steal_coef-0.1) / steal_coef))
					v.add(new Eventing("You attacked " + i + " with " + (-tokens[humanIndex][i]) + " tokens", baseline - didTake));
				else if (ratio > (0.8 / steal_coef))
					v.add(new Eventing("You attacked " + i + " with " + (-tokens[humanIndex][i]) + " tokens (they partially blocked it)", baseline - didTake));
				else if (ratio > (0.05 / steal_coef))
					v.add(new Eventing("You attacked " + i + " with " + (-tokens[humanIndex][i]) + " tokens (they mostly blocked it)", baseline - didTake));
				else
					v.add(new Eventing("You attacked " + i + " with " + (-tokens[humanIndex][i]) + " tokens (they blocked it)", baseline - didTake));
			}
		}

		return v;
	}

	public Vector<Eventing> getAttacksCarriedOut_others(int numTokens, int idx, int[][] inferredTokens) {
		Vector<Eventing> v = new Vector<>();
		double shouldaTaken, didTake, baseline, ratio;

		for (int i = 0; i < numPlayers; i++) {
			if (inferredTokens[idx][i] < 0) {
				shouldaTaken = steal_coef * popularities[round-1][idx] * (inferredTokens[idx][i] / ((double)numTokens)) * alpha;
				baseline = popularities[round-1][idx] * (inferredTokens[idx][i] / ((double)numTokens)) * alpha;
				didTake = influence[idx][i] - (prevInfluence[idx][i] * (1.0 - alpha));
				ratio = didTake / shouldaTaken;
				if (ratio > ((steal_coef-0.1) / steal_coef))
					v.add(new Eventing("attacked " + i + " with " + (-inferredTokens[idx][i]) + " tokens", baseline - didTake));
				else if (ratio > (0.8 / steal_coef))
					v.add(new Eventing("attacked " + i + " with " + (-inferredTokens[idx][i]) + " tokens (" + i + " partially blocked it)", baseline - didTake));
				else if (ratio > (0.05 / steal_coef))
					v.add(new Eventing("attacked " + i + " with " + (-inferredTokens[idx][i]) + " tokens (" + i + " mostly blocked it)", baseline - didTake));
				else
					v.add(new Eventing("attacked " + i + " with " + (-inferredTokens[idx][i]) + " tokens (" + i + " blocked it)", baseline - didTake));
			}
		}

		return v;
		// Vector<Eventing> v = new Vector<>();
		// double stealWorth = steal_coef * popularities[round-1][idx] * (1.0 / numTokens) * alpha;
		// double baseline = popularities[round-1][idx] * (1.0 / numTokens) * alpha;

		// int tokensRemaining = numTokens;
		// Set<Integer> mayHaveAttacked = new TreeSet<Integer>();
		// for (int i = 0; i < numPlayers; i++) {
		// 	tokensRemaining -= inferredTokens[idx][i];
		// 	if ((influence[idx][i] + (0.5 * stealWorth)) < (prevInfluence[idx][i] * (1.0 - alpha))) {
		// 		mayHaveAttacked.add(i);
		// 	}
		// }

		// if (tokensRemaining > 0) {
		// 	if (mayHaveAttacked.size() > 0) {
		// 		double totalAttack = 0.0;//amountStolen[round][idx] - ((1.0 - alpha) * amountStolen[round-1][idx]);
		// 		double taken, profit;
		// 		Iterator<Integer> itr = mayHaveAttacked.iterator();
		// 		int current;
		// 		while(itr.hasNext()){
		// 			current = itr.next();
		// 			totalAttack -= (influence[idx][current] - (prevInfluence[idx][current] * (1.0 - alpha)));
		// 		}
		// 		double value = totalAttack - (baseline * tokensRemaining);
		// 		if (value < 0.0) {
		// 			if (mayHaveAttacked.size() == 1)
		// 				v.add(new Eventing("Attack on " + mayHaveAttacked + " with " + tokensRemaining + " tokens (substantially blocked)", value));
		// 			else
		// 				v.add(new Eventing("Attacks on " + mayHaveAttacked + " with " + tokensRemaining + " tokens (substantially blocked)", value));
		// 		}
		// 		else {
		// 			if (mayHaveAttacked.size() == 1)
		// 				v.add(new Eventing("Attack on " + mayHaveAttacked + " with " + tokensRemaining + " tokens", value));
		// 			else
		// 				v.add(new Eventing("Attacks on " + mayHaveAttacked + " with " + tokensRemaining + " tokens", value));
		// 		}
		// 	}
		// 	else if (tokensRemaining > 1) {
		// 		v.add(new Eventing("Blocked attack on unknown player with " + tokensRemaining + " tokens",  -(baseline * tokensRemaining)));
		// 	}
		// }

		// return v;
	}

	public Vector<Eventing> getKeeping_self(int numTokens) {
		Vector<Eventing> v = new Vector<>();

		if (tokens[humanIndex][humanIndex] > 0) {
			double baseline = popularities[round-1][humanIndex] * (tokens[humanIndex][humanIndex] / ((double)numTokens)) * alpha;
			double didGet = keep_coef * popularities[round-1][humanIndex] * (tokens[humanIndex][humanIndex] / ((double)numTokens)) * alpha;
			if (tokens[humanIndex][humanIndex] > 1)
				v.add(new Eventing("You kept " + tokens[humanIndex][humanIndex] + " tokens in the last round", didGet - baseline));
			else
				v.add(new Eventing("You kept " + tokens[humanIndex][humanIndex] + " token in the last round", didGet - baseline));
		}

		return v;
	}

	public Vector<Eventing> getKeeping_others(int numTokens, int idx, int[][] inferredTokens) {
		Vector<Eventing> v = new Vector<>();

		// double keepAmount = (influence[idx][idx] + amountStolen[round][idx]) - ((prevInfluence[idx][idx] + amountStolen[round-1][idx]) * (1.0 - alpha));
		// double keepWorth = keep_coef * popularities[round-1][idx] * (1.0 / numTokens) * alpha;

		int numKept = inferredTokens[idx][idx]; //(int)((keepAmount / keepWorth) + 0.5);

		if (numKept > 0) {
			double baseline = popularities[round-1][idx] * (numKept / ((double)numTokens)) * alpha;
			double didGet = keep_coef * popularities[round-1][idx] * (numKept / ((double)numTokens)) * alpha;
			if (numKept > 1)
				v.add(new Eventing("" + idx + " kept " + numKept + " tokens in the last round", didGet - baseline));
			else
				v.add(new Eventing("" + idx + " kept " + numKept + " token in the last round", didGet - baseline));
		}

		return v;
	}

	public Vector<Eventing> getReputation(int numTokens, double cambio, double other) {
		Vector<Eventing> v = new Vector<>();

		v.add(new Eventing("Popularity adjustments due to how current popularity standings", cambio - other));
		v.add(new Eventing("  impact views of exchanges made in previous rounds", -99999));
		// double impact, wouldaBeen, isDifference, mine = 0.0;

		// if (round < 2)
		// 	return v;

		// double impactMe = 0.0;
		// for (int i = 0; i < numPlayers; i++) {
		// 	if (i != humanIndex) {
		// 		if (tokens[i][humanIndex] > 0)
		// 			impact = give_coef * popularities[round-1][i] * tokens[i][humanIndex] / ((double)numTokens);
		// 		else if (tokens[i][humanIndex] < 0)
		// 			impact = stealCoef(humanIndex) * popularities[round-1][i] * tokens[i][humanIndex] / ((double)numTokens);
		// 		else
		// 			impact = 0.0;
		// 		wouldaBeen = alpha * impact + (1.0 - alpha) * prevInfluence[i][humanIndex];
		// 		isDifference = influence[i][humanIndex] - wouldaBeen;

		// 		// if (influence[humanIndex][i] < 0.0) {
		// 		// 	if (tokens[humanIndex][i] > 0)
		// 		// 		impact = give_coef * popularities[round-1][i] * tokens[humanIndex][i] / ((double)numTokens);
		// 		// 	else if (tokens[humanIndex][i] < 0)
		// 		// 		impact = stealCoef(humanIndex) * popularities[round-1][i] * tokens[humanIndex][i] / ((double)numTokens);
		// 		// 	else
		// 		// 		impact = 0.0;
		// 		// 	wouldaBeen = alpha * impact + (1.0 - alpha) * prevInfluence[humanIndex][i];
		// 		// 	mine -= influence[humanIndex][i]; //(influence[humanIndex][i] - wouldaBeen) + (influence[humanIndex][i] - prevInfluence[humanIndex][i]);
		// 		// 	// System.out.println("" + i + " error: " + (influence[humanIndex][i] - wouldaBeen));
		// 		// 	// System.out.println("" + i + " influence: " + (influence[humanIndex][i] - prevInfluence[humanIndex][i]));
		// 		// 	isDifference -= influence[humanIndex][i] - wouldaBeen;
		// 		// }

		// 		if (Math.abs(isDifference) > 0.05) {
		// 			if (influence[i][humanIndex] >= 0.0)
		// 				v.add(new Eventing("due to your association with " + i, isDifference));
		// 			else
		// 				v.add(new Eventing("due to your conflict with " + i, isDifference));
		// 		}

		// 		if (tokens[humanIndex][i] < 0)
		// 			// Can't do this
		// 			impactMe -= stealCoef(i) * popularities[round-1][humanIndex] * tokens[humanIndex][i] / ((double)numTokens);
		// 	}
		// 	else {
		// 		if (tokens[humanIndex][humanIndex] > 0)
		// 			impactMe += keep_coef * popularities[round-1][humanIndex] * tokens[humanIndex][humanIndex] / ((double)numTokens);
		// 	}
		// }

		// // if (tokens[humanIndex][humanIndex] > 0)
		// // 	impact = keep_coef * popularities[round-1][humanIndex] * tokens[humanIndex][humanIndex] / ((double)numTokens);
		// // else
		// // 	impact = 0.0;
		// wouldaBeen = alpha * impactMe + (1.0 - alpha) * prevInfluence[humanIndex][humanIndex];

		// // System.out.println("impactMe: " + impactMe);
		// // System.out.println("previnfluence: " + prevInfluence[humanIndex][humanIndex]);
		// // System.out.println("wouldaBeen: " + wouldaBeen);
		// // System.out.println("own influence: " + influence[humanIndex][humanIndex]);
		// // System.out.println("own influence on 6: " + influence[humanIndex][6]);
		// // System.out.println("mine: " + mine);

		// isDifference = influence[humanIndex][humanIndex] - wouldaBeen;// - mine;
		// if (Math.abs(isDifference) > 0.05)
		// 	v.add(new Eventing("due to yourself", isDifference));

		return v;
	}

	public double stealCoef(int attackedIdx) {
		double keepStrength = tokens[attackedIdx][attackedIdx] * popularities[round-1][attackedIdx];
		double attackStrength = 0.0;
		for (int i = 0; i < numPlayers; i++) {
			if (tokens[i][attackedIdx] < 0)
				attackStrength += (-tokens[i][attackedIdx]) * popularities[round-1][i];
		}

		if (attackStrength == 0)
			return steal_coef;
			
		double coef = 1 - (keepStrength / attackStrength);
		if (coef > 0.0)
			return steal_coef * coef;
		else
			return 0.0;
	}

	// public String getListString(Vector<Integer> v) {
	// 	String str = "<";
	// 	for (int i = 0; i < v.size(); i++) {
	// 		if (i != (v.size()-1))
	// 			str += "" + v.get(i) + ", ";
	// 		else
	// 			str += "" + v.get(i);
	// 	}
	// 	str += ">";

	// 	return str;
	// }

	public void drawPopularityGraph(Graphics g) {
		g.setColor(new Color(255, 255, 255));
		g.drawLine(760, 85, 760, 60 + numPlayers * 25);
		g.drawLine(760, 60 + numPlayers * 25, 1180, 60 + numPlayers * 25);

		if (round > 0) {
			int valInc = 1;
			double distInc = 420.0 / round;
			if (round > 15) {
				valInc = 5;
				//distInc = (420.0 / round) * 5;
			}

			// draw x-axis tick labels
			g.setFont(new Font("Courier", Font.PLAIN, 12));
			for (int i = 0; i <= round; i+=valInc) {
				//System.out.println(""+i);
				//if (round > 15)
				//	g.drawString(""+i, 756+(int)(distInc/5.0*i+0.5), 73 + numPlayers * 25);
				//else
					g.drawString(""+i, 756+(int)(distInc*i+0.5), 73 + numPlayers * 25);
			}

			double maxP = 1.0;
			for (int i = 0; i < numPlayers; i++) {
				for (int j = 0; j <= round; j++) {
					if (popularities[j][i] > maxP)
						maxP = popularities[j][i];
				}
			}

			double popScale = (numPlayers * 25 - 35) / maxP;

			int x1, y1, x2, y2;
			for (int i = 0; i < numPlayers; i++) {
				g.setColor(theColors[i]);
				for (int j = 1; j <= round; j++) {
					x1 = 761 + (int)((j-1) * distInc + 0.5);
					x2 = 761 + (int)(j * distInc + 0.5);
					y1 = (60 + numPlayers * 25) - (int)(popularities[j-1][i] * popScale + 0.5);
					y2 = (60 + numPlayers * 25) - (int)(popularities[j][i] * popScale + 0.5);
					g.drawLine(x1, y1, x2, y2);
				}
			}
		}
	}

	public void drawPopMsg(Graphics g) {
		if (!popMsg.equals("")) {
			g.setColor(new Color(230, 230, 230));
			if (popMsg.length() == 1)
				g.fillRect(mousePunto.x, mousePunto.y-17, 13, 16);
			else
			g.fillRect(mousePunto.x, mousePunto.y-17, 22, 16);
			g.setColor(new Color(70, 70, 70));
			g.setFont(new Font("Arial", Font.PLAIN, 15));
			g.drawString(popMsg, mousePunto.x+2, mousePunto.y-3);
		}
	}

	void drawPlayer(Graphics g, int id, int cy, double tornadoAmplification) {
		if (id == descriptionIdx) {
			g.setColor(new Color(80, 80, 80));
			g.fillRect(13, cy-2, 248, 21);
		}

		//setMyColor(g, id);
		g.setColor(theColors[id]);
		g.fillRect(17, cy, 37, 17);

		g.setFont(new Font("Arial", Font.PLAIN, 15));
		if (((id % 2) == 0) || (id >= 10))
			g.setColor(new Color(0, 0, 0));
		else
			g.setColor(new Color(255, 255, 255));

		if (id == humanIndex) {
			String str = "You";
			g.drawString(str, 22, cy+14);
		}
		else {
			String str = "" + id;
			if (id < 10)
				g.drawString(str, 31, cy+14);
			else
				g.drawString(str, 26, cy+14);
		}

		// start: the visualTrait
		// g.setColor(new Color(150, 150, 150));
		// g.drawRect(60, cy+1, 15, 15);

		int rd, grn, bl;
		if (visualTraits[id] >= 100) {
			rd = 0;
			grn = 255;
			bl = 0;
		}
		else {
			double scle = visualTraits[id] / 100.0;
			rd = (int)((1-scle) * 255.0);
			grn = 0;
			bl = (int)(scle * 255.0);
		}

		g.setColor(new Color(rd, grn, bl));
		g.fillRect(60, cy+1, 15, 15);
		// end: the visualTrait

		g.setFont(new Font("Courier", Font.PLAIN, 12));
		g.setColor(new Color(255, 255, 255));

		g.drawString(String.format("%1$,.2f", popularities[round][id]), 96, cy+12);

		String dado = "" + tokens[humanIndex][id];
		if (tokens[humanIndex][id] < 0)
			g.drawString(dado, 168, cy+12);
		else
			g.drawString(dado, 175, cy+12);

		String recibido = "" + tokens[id][humanIndex];
		if (tokens[id][humanIndex] < 0)
			g.drawString(recibido, 226, cy+12);
		else
			g.drawString(recibido, 233, cy+12);

		if (humanIndex != id) {
			if (!gameOver)
				g.setColor(new Color(200, 50, 50));
			else
				g.setColor(new Color(150, 150, 150));
			g.fillRect(minusButtons[id].x - minusButtons[id].w/2, minusButtons[id].y - minusButtons[id].h/2, minusButtons[id].w, minusButtons[id].h);
			g.setColor(new Color(230, 230, 230));
			g.drawLine(minusButtons[id].x-4, minusButtons[id].y, minusButtons[id].x+4, minusButtons[id].y);

			if (!gameOver)
				g.setColor(new Color(100, 200, 100));
			else
				g.setColor(new Color(150, 150, 150));
			g.fillRect(plusButtons[id].x - plusButtons[id].w/2, plusButtons[id].y - plusButtons[id].h/2, plusButtons[id].w, plusButtons[id].h);
			g.setColor(new Color(0, 0, 0));
			g.drawLine(plusButtons[id].x-4, plusButtons[id].y, plusButtons[id].x+4, plusButtons[id].y);
			g.drawLine(plusButtons[id].x, plusButtons[id].y-4, plusButtons[id].x, plusButtons[id].y+4);
		}

		g.setColor(new Color(255, 255, 255));
		String str = "" + allocations[id];
		if (str.length() == 1)
			g.drawString(str, 314, cy+12);
		else if (str.length() == 2)
			g.drawString(str, 310, cy+12);
		else
		g.drawString(str, 306, cy+12);

		// draw tornado
		if (round > 0) {
			int posBase = 561, negBase = 559;

			// first draw the initial popularity influence
			int w2 = (int)(influence[numPlayers][id] * tornadoAmplification + 0.5);
			g.setColor(new Color(80, 80, 80));
			drawInitialTornadoValue(g, posBase, cy, w2, 16, numPlayers);
			posBase += w2;

			for (int j = 0; j < numPlayers; j++) {
				if (influence[j][id] > 0) {
					int w = (int)(influence[j][id] * tornadoAmplification + 0.5);
					if (w > 0) {
						g.setColor(theColors[j]);
						drawTornadoValue(g, posBase, cy, w, 16, j);
						//g.fillRect(posBase - w, cy, w, 16);
						posBase += w;
					}
				}
				else {
					int w = (int)(-influence[j][id] * tornadoAmplification + 0.5);
					//System.out.println(w);
					if (w > 0) {
						g.setColor(theColors[j]);
						drawTornadoValue(g, negBase - w, cy, w, 16, j);
						//g.fillRect(negBase, cy, w, 16);
						negBase -= w;
					}
				}
			}
		}
	}

	public void drawTornadoValue(Graphics g, int x, int y, int w, int h, int index) {
		g.fillRect(x, y, w, h);

		double dx = mousePunto.x - x;
		double dy = mousePunto.y - y;

		if ((dx > 0) && (dx < w) && (dy > 0) && (dy < h)) {
			popMsg = "" + index;
		}
	}

	public void drawInitialTornadoValue(Graphics g, int x, int y, int w, int h, int index) {
		g.fillRect(x, y, w, h);
		g.setColor(new Color(200, 200, 200));
		g.drawRect(x, y+1, w, h-2);
		for (int i = x+5; i < (x-5)+w; i+= 10) {
			g.drawLine(i, y+(h-2), i+6, y+1); 
		}

		double dx = mousePunto.x - x;
		double dy = mousePunto.y - y;

		if ((dx > 0) && (dx < w) && (dy > 0) && (dy < h)) {
			popMsg = "Init";
		}
	}


	public void drawHeaders(Graphics g) {
		g.setFont(new Font("Arial", Font.PLAIN, 20));
		g.setColor(new Color(255, 255, 255));
		String str;
		if (gameOver)
			str = "Round " + round + " (Game Over)";
		else
			str = "Round " + (round+1);
		g.drawString(str, 10, 30);

		g.setFont(new Font("Courier", Font.PLAIN, 12));
		g.drawString("Player", 15, 67);
		g.drawString("Popularity", 75, 67);
		g.drawString("Sent", 165, 67);
		g.drawString("Received", 210, 67);
		g.drawString("Allocations", 280, 67);
		g.drawString("Negative Influence", 410, 67);
		g.drawString("Positive Influence", 585, 67);
		g.drawString("Popularity History", 770, 67);

		//g.drawLine(385, 75, 385, 100);
		//g.drawLine(535, 75, 535, 100);
		g.drawLine(560, 75, 560, 82 + numPlayers * 25);

		g.drawLine(10, 51, 1190, 51);
		g.drawLine(10, 75, 1190, 75);
		g.drawLine(10, 82 + numPlayers * 25, 1190, 82 + numPlayers * 25);

		if (!gameOver) {
			g.setColor(new Color(255, 255, 255));
			g.drawRect(submit.x - submit.w/2, submit.y - submit.h/2, submit.w, submit.h);
			g.setFont(new Font("Arial", Font.PLAIN, 18));
			g.drawString("Submit", submit.x - 28, submit.y+6);
		}
	}
}

class Human extends JFrame implements ComponentListener, MouseListener {
    myCanvas canvas;
    Color bkgroundColor = new Color(0, 0, 0);
	boolean shown = false;

    Human() {
		int numPlayers = determineNumPlayers();

		int _screenWidth = 1200;
		// int _screenHeight = 135 + numPlayers * 25;
		int _screenHeight = 135 + numPlayers * 25 + 400;

        setSize(_screenWidth, _screenHeight + 22);
        getContentPane().setBackground(bkgroundColor);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(100, 0, _screenWidth, _screenHeight + 22);
        canvas = new myCanvas(numPlayers);
		addMouseListener(this);
		addComponentListener(this);
        getContentPane().add(canvas);
        setVisible(true);
        setTitle("The Human Interface");

		shown = true;
    }

	public int determineNumPlayers() {
		int numPlayers = -1;
		try {
			String file = "../State/state.txt";
			BufferedReader reader = new BufferedReader(new FileReader(file));
			String str;

			// get game info
			str = reader.readLine();
			numPlayers = Integer.parseInt(reader.readLine());

			reader.close();
		}
		catch (IOException e) {
			System.out.println(e);
		}

		return numPlayers;
	}

	public void componentHidden(ComponentEvent e) {}
    public void componentResized(ComponentEvent e) {}
    public void componentShown(ComponentEvent e) {}

    public void componentMoved(ComponentEvent e) {
		if (!shown)
			return;

		Point p = getContentPane().getLocationOnScreen();
		canvas.updateScreenPosition(p.x, p.y);
    }


	public void mousePressed(MouseEvent e) {
		boolean isLeft = true;
		if (SwingUtilities.isRightMouseButton(e)) {
			//System.out.println("Mouse clicked: " + e.getX() + ", " + e.getY());
			isLeft = false;
		}
	
		canvas.theClick(isLeft, e.getX(), e.getY()-25);
	}

	public void mouseReleased(MouseEvent e) {}
	public void mouseEntered(MouseEvent e) {}
	public void mouseExited(MouseEvent e) {}
	public void mouseClicked(MouseEvent e) {}

	public static void main(String args[]) {
        new Human();
    }
}
