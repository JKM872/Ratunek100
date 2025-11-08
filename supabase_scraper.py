"""
Supabase Direct Integration for LiveSport Scraper
Sends matches directly to Supabase PostgreSQL (faster than webhook)
"""

import os
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime
import json

class SupabaseIntegrator:
    """Direct Supabase integration - no webhook needed"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://bfslhqnxsgmdyptrqshj.supabase.co')
        self.supabase_key = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmc2xocW54c2dtZHlwdHJxc2hqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2MDU3NTYsImV4cCI6MjA3ODE4MTc1Nn0.QMiCdK8L-UFjeTAT9a5sPzXo_A8azpZe3p4SnfM0Fi8')
        
        self.supabase: Optional[Client] = None
        
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            print('✅ Supabase client initialized')
            print(f'   URL: {self.supabase_url}')
        except Exception as e:
            print(f'❌ Supabase initialization error: {e}')
            self.supabase = None
    
    def send_matches(self, matches: List[Dict], date: str, sport: str) -> Dict:
        """
        Send matches directly to Supabase database
        
        Args:
            matches: List of match dictionaries
            date: Match date (YYYY-MM-DD)
            sport: Sport name or comma-separated sports
        
        Returns:
            Dict with success status and statistics
        """
        
        if not self.supabase:
            print('❌ Supabase client not available')
            return {'success': False, 'error': 'Supabase not initialized'}
        
        if not matches:
            print('⚠️  No matches to send')
            return {'success': False, 'error': 'No matches provided'}
        
        try:
            print('\n' + '='*70)
            print('📤 SUPABASE: Sending matches directly to cloud database')
            print('='*70)
            print(f'📅 Date: {date}')
            print(f'⚽ Sport(s): {sport}')
            print(f'📊 Total matches: {len(matches)}')
            print(f'🌐 Database: Supabase PostgreSQL (persistent)')
            
            # Prepare data for Supabase
            supabase_matches = []
            for match in matches:
                # Convert all_odds to JSON string if it's a dict
                all_odds_json = match.get('all_odds')
                if all_odds_json and isinstance(all_odds_json, dict):
                    all_odds_json = json.dumps(all_odds_json)
                elif all_odds_json and isinstance(all_odds_json, str):
                    # Already JSON string
                    pass
                else:
                    all_odds_json = None
                
                supabase_matches.append({
                    'sport': match.get('sport') or sport,
                    'match_date': match.get('match_date') or date,
                    'match_time': match.get('match_time'),
                    'home_team': match.get('home_team'),
                    'away_team': match.get('away_team'),
                    'home_odds': match.get('home_odds'),
                    'away_odds': match.get('away_odds'),
                    'draw_odds': match.get('draw_odds'),
                    'home_win_percentage': match.get('home_win_percentage'),
                    'draw_percentage': match.get('draw_percentage'),
                    'away_win_percentage': match.get('away_win_percentage'),
                    'avg_home_goals': match.get('avg_home_goals'),
                    'avg_away_goals': match.get('avg_away_goals'),
                    'qualifies': match.get('qualifies', 0),
                    'created_at': match.get('created_at') or datetime.utcnow().isoformat(),
                    'all_odds': all_odds_json,
                    'bookmaker_name': match.get('bookmaker_name'),
                    'bookmaker_url': match.get('bookmaker_url')
                })
            
            # Batch insert (50 per batch for optimal performance)
            saved = 0
            duplicates = 0
            errors = 0
            BATCH_SIZE = 50
            
            total_batches = (len(supabase_matches) + BATCH_SIZE - 1) // BATCH_SIZE
            
            for i in range(0, len(supabase_matches), BATCH_SIZE):
                batch = supabase_matches[i:i+BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1
                
                print(f'   📦 Batch {batch_num}/{total_batches} ({len(batch)} matches)...')
                
                try:
                    # Try batch upsert first
                    response = self.supabase.table('matches').upsert(
                        batch,
                        on_conflict='sport,home_team,away_team,match_time'
                    ).execute()
                    
                    saved += len(batch)
                    print(f'      ✅ Upserted {len(batch)} matches')
                    
                except Exception as e:
                    error_msg = str(e)
                    
                    # If batch fails, try one by one (to handle duplicates properly)
                    print(f'      ⚠️  Batch failed, trying individual inserts...')
                    
                    for match in batch:
                        try:
                            self.supabase.table('matches').insert(match).execute()
                            saved += 1
                        except Exception as e2:
                            error_msg2 = str(e2)
                            
                            # Check if duplicate key error (PostgreSQL error code 23505)
                            if '23505' in error_msg2 or 'duplicate' in error_msg2.lower() or 'unique' in error_msg2.lower():
                                duplicates += 1
                            else:
                                print(f'         ❌ Error: {error_msg2[:100]}')
                                errors += 1
            
            print(f'\n{"="*70}')
            print(f'✅ SUPABASE SYNC COMPLETE')
            print(f'{"="*70}')
            print(f'   💾 Saved: {saved}')
            print(f'   🔄 Duplicates skipped: {duplicates}')
            print(f'   ❌ Errors: {errors}')
            print(f'   📊 Total processed: {len(matches)}')
            print(f'{"="*70}\n')
            
            return {
                'success': True,
                'saved': saved,
                'duplicates': duplicates,
                'errors': errors,
                'total': len(matches),
                'database': 'supabase'
            }
            
        except Exception as e:
            print(f'\n❌ FATAL ERROR in Supabase sync: {e}')
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'saved': 0,
                'duplicates': 0,
                'errors': len(matches)
            }
    
    def get_match_count(self) -> Optional[int]:
        """Get total number of matches in Supabase"""
        
        if not self.supabase:
            return None
        
        try:
            response = self.supabase.table('matches').select('id', count='exact').execute()
            return response.count
        except Exception as e:
            print(f'❌ Error getting match count: {e}')
            return None
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        
        if not self.supabase:
            print('❌ Supabase client not initialized')
            return False
        
        try:
            count = self.get_match_count()
            if count is not None:
                print(f'✅ Supabase connection OK - {count} matches in database')
                return True
            else:
                print('❌ Supabase connection failed')
                return False
        except Exception as e:
            print(f'❌ Connection test failed: {e}')
            return False


def get_supabase_integrator() -> SupabaseIntegrator:
    """Factory function - returns configured Supabase integrator"""
    return SupabaseIntegrator()


# Test script
if __name__ == '__main__':
    print('🧪 Testing Supabase integration...\n')
    
    integrator = get_supabase_integrator()
    
    # Test connection
    if integrator.test_connection():
        print('\n✅ Supabase integration ready to use!')
        
        # Test data
        test_matches = [
            {
                'sport': 'Football',
                'match_date': '2025-11-09',
                'match_time': '20:00',
                'home_team': 'Test Home Team',
                'away_team': 'Test Away Team',
                'home_odds': 2.10,
                'away_odds': 3.50,
                'draw_odds': 3.20,
                'avg_home_goals': 1.8,
                'avg_away_goals': 1.2,
                'qualifies': 1
            }
        ]
        
        print('\n🧪 Sending test match...')
        result = integrator.send_matches(test_matches, '2025-11-09', 'Football')
        
        if result['success']:
            print(f'\n✅ Test successful! Check Supabase dashboard.')
        else:
            print(f'\n❌ Test failed: {result.get("error")}')
    else:
        print('\n❌ Supabase integration not available')
