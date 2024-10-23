#include <iostream>
#include <cmath>
#include <map>
#include <set>
#include <algorithm>
#include <vector>
#include <string>
#include <sstream>
#include <fstream>
#include <random>

using namespace std;


const int nodes = 6;
const int edges = nodes - 1;


void generate_edge_labels(map<pair<int,int>, int> &edge_labels,map<int, pair<int,int>> &label_to_edge, vector<vector<int>> &a){
	int idx = 1;
	for(int i = 0; i < nodes; i++){
		for(auto j : a[i])
		if(edge_labels[{i,j}]==0){
			edge_labels[{i,j}] = idx;
			edge_labels[{j,i}] = idx;
			label_to_edge[idx] = {i,j};
			idx++;
		}
	}
	return;
}

vector<int> get_state(int n){
	vector<int> result(nodes-1);
	for(int i = 0; i < nodes-1; i++){
		result[i] = n%2;
		n /= 2;
	}
	return result;
}

int get_idx(vector<int> state){
	int result = 0;
	for(int i = 0; i < state.size(); i++){
		if(state[i]==1) result += (1<<i);
	}
	return result;
}

void write_to_file(char (&matrix)[(1<<(nodes-1))][(1<<(nodes-1))]){
	ofstream file;
	file.open("matrix.txt");
	for(int i = 0; i < (1<<(nodes-1)); i++){
		for(int j = 0; j < (1<<(nodes-1)); j++){
			file<<matrix[i][j]<<" ";
		}
		file<<endl;
	}
	return;
}


int main(){//all of this is for Type I fusion
	
	
	vector<pair<int,int> >target_tree;
	
	map<pair<int,int>, bool> edge_present;
	map<pair<int,int>, int> edge_labels;
	map<int, pair<int,int>> label_to_edge;
	

	char matrix[(1<<(nodes-1))][(1<<(nodes-1))];
	
	
	vector<vector<int>> a(nodes);
	// define tree
	// a[0] = {1,2}; a[1] = {0,3,4,5}; a[2] = {0,6}; a[3] = {1,7,8,9}; a[4] = {1}; a[5] = {1}; a[6] = {2,10,11}; a[7] = {3}; a[8] = {3}; a[9] = {3}; a[10] = {6}; a[11] = {6};
	
	//line
	a[0] = {1};
	a[nodes-1] = {nodes-2};
	for(int i = 1; i < nodes-1; i++) a[i] = {i-1,i+1};
	
	generate_edge_labels(edge_labels,label_to_edge, a);//run from 1...nodes
	////////////////////
	//  Create Matrix //
	////////////////////

	for(int i = 0; i < (1<<(nodes-1)); i++){
		for(int j = 0; j < (1<<(nodes-1)); j++){
			matrix[i][j] = '0';
		}
	}
	for(int i = 0; i < (1<<(nodes-1));i++){
		vector<int> state = get_state(i);
		vector<int> state_copy = state;

		//this part contains the core of the instructions to build the tree
		//there are many other options, we have to discuss this further

		for(int j = 0; j < state.size(); j++){
			state_copy = state;
			if (state_copy[j] == 1) continue;
			
			//in case of success
			state_copy[j] = 1;
			int idx = get_idx(state_copy);
			matrix[idx][i] = 'p';
			state_copy = state;
			

			//in case of failure, the edge stays zero and the neighboring edges all become zero
			int node_1 = label_to_edge[j+1].first;
			int node_2 = label_to_edge[j+1].second;
			//set also neighboring edges to 0
			for(auto nn : a[node_1]){
				// cout<<node_1<<" "<<nn<<" "<<edge_labels[{node_1,nn}]<<endl;
				state_copy[edge_labels[{node_1,nn}]-1] = 0;
			}
			for(auto nn : a[node_2]){
				state_copy[edge_labels[{node_2,nn}]-1] = 0;
			}
			idx = get_idx(state_copy);
			matrix[idx][i] = 'q';
			break;
		}
	}
	cout<<(1<<(nodes-1))-1<<endl;
	matrix[(1<<(nodes-1))-1][(1<<(nodes-1))-1] = '1';
	write_to_file(matrix);
	return 0;
}
