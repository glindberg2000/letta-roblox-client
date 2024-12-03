#!/usr/bin/env python3
"""
Tool for managing Letta agents.
"""
import argparse
import json
import sys
from typing import Dict, List
import requests
from letta_roblox.client import LettaRobloxClient

class AgentManager:
    def __init__(self, server_url: str = "http://localhost:8283"):
        self.client = LettaRobloxClient(server_url)
        
    def check_server(self) -> bool:
        """Verify Letta server is running."""
        try:
            # Try health endpoint first
            try:
                response = requests.get(f"{self.client.base_url}/health", timeout=5)
                response.raise_for_status()
                print("✓ Letta server is running (health check)")
                return True
            except requests.exceptions.RequestException:
                # If health endpoint fails, try listing agents
                response = requests.get(
                    f"{self.client.base_url}/v1/agents",
                    headers=self.client.headers
                )
                response.raise_for_status()
                print("✓ Letta server is running (API check)")
                return True
            
        except requests.ConnectionError:
            print("\n✗ Error: Could not connect to Letta server")
            print(f"  URL: {self.client.base_url}")
            print("\nTroubleshooting steps:")
            print("  1. Check if Docker is running:")
            print("     $ docker ps | grep letta")
            print("  2. Check server logs:")
            print("     $ docker logs letta")
            print("  3. Try accessing directly:")
            print(f"     $ curl {self.client.base_url}/v1/agents")
            return False
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            print(f"  Server URL: {self.client.base_url}")
            print("  Headers:", self.client.headers)
            return False

    def list_agents(self, verbose: bool = False) -> List[Dict]:
        """List all agents and their details."""
        try:
            # Get list of agents
            url = f"{self.client.base_url}/v1/agents"
            response = requests.get(url, headers=self.client.headers)
            response.raise_for_status()
            agents = response.json()
            
            print("\nLetta Agents:")
            print("=" * 80)
            
            for agent in agents:
                print(f"ID: {agent['id']}")
                print(f"Name: {agent['name']}")
                print(f"Created: {agent['created_at']}")
                
                # Get memory details
                memory_url = f"{self.client.base_url}/v1/agents/{agent['id']}/memory"
                memory_response = requests.get(memory_url, headers=self.client.headers)
                if memory_response.ok:
                    memory = memory_response.json()
                    if 'memory' in memory:
                        print("\nMemory:")
                        for block in memory['memory'].values():
                            print(f"{block['label'].title()}: {block['value']}")
                
                print("-" * 80)
            
            return agents
            
        except Exception as e:
            print(f"Error listing agents: {e}")
            return []

    def get_agent(self, agent_id: str) -> Dict:
        """Get detailed info for a specific agent."""
        try:
            # Get agent details
            url = f"{self.client.base_url}/v1/agents/{agent_id}"
            response = requests.get(url, headers=self.client.headers)
            response.raise_for_status()
            agent = response.json()
            
            print("\nAgent Details:")
            print("=" * 80)
            print(f"ID: {agent['id']}")
            print(f"Name: {agent['name']}")
            print(f"Created: {agent['created_at']}")
            
            # Get memory
            memory_url = f"{self.client.base_url}/v1/agents/{agent_id}/memory"
            memory_response = requests.get(memory_url, headers=self.client.headers)
            if memory_response.ok:
                memory = memory_response.json()
                if 'memory' in memory:
                    print("\nMemory:")
                    for block in memory['memory'].values():
                        print(f"{block['label'].title()}: {block['value']}")
            
            return agent
            
        except Exception as e:
            print(f"Error getting agent {agent_id}: {e}")
            return {}

    def delete_agent(self, agent_id: str) -> bool:
        """Delete a specific agent."""
        try:
            self.client.delete_agent(agent_id)
            print(f"✓ Deleted agent: {agent_id}")
            return True
        except Exception as e:
            print(f"✗ Error deleting agent {agent_id}: {e}")
            return False

    def delete_all_agents(self) -> None:
        """Delete all agents after confirmation."""
        agents = self.list_agents()
        
        if not agents:
            print("No agents found.")
            return
            
        if input("\nAre you sure you want to delete all agents? (y/N) ").lower() != 'y':
            print("Aborted.")
            return
            
        for agent in agents:
            self.delete_agent(agent['id'])
        
        print("\nAll agents deleted.")

def main():
    parser = argparse.ArgumentParser(
        prog='letta-manage',  # Use correct program name
        description='Manage Letta agents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  List all agents:
    letta-manage list
    
  List agents with memory details:
    letta-manage list --verbose
    
  Get specific agent:
    letta-manage get --id agent-123
    
  Delete agent:
    letta-manage delete --id agent-123
    
  Delete all agents:
    letta-manage delete-all
        """
    )
    
    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest='action', required=True)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all agents')
    list_parser.add_argument('--verbose', '-v', action='store_true',
                          help='Show detailed information')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get agent details')
    get_parser.add_argument('--id', required=True,
                         help='Agent ID to get details for')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete an agent')
    delete_parser.add_argument('--id', required=True,
                           help='Agent ID to delete')
    
    # Delete-all command
    subparsers.add_parser('delete-all', help='Delete all agents')
    
    # Global options
    parser.add_argument('--server', default='http://localhost:8283',
                      help='Letta server URL')
    
    args = parser.parse_args()
    
    manager = AgentManager(args.server)
    
    if not manager.check_server():
        sys.exit(1)
    
    if args.action == 'list':
        if args.verbose:
            manager.list_agents(verbose=True)
        else:
            manager.list_agents(verbose=False)
    elif args.action == 'get':
        manager.get_agent(args.id)
    elif args.action == 'delete':
        manager.delete_agent(args.id)
    elif args.action == 'delete-all':
        manager.delete_all_agents()

if __name__ == "__main__":
    main() 