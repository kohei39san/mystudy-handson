import json
import sys
import traceback

def lambda_handler(event, context):
    """Simple Lambda function to test pydantic and psycopg2-binary imports"""
    
    results = {
        'statusCode': 200,
        'timestamp': getattr(context, 'aws_request_id', 'test'),
        'python_version': sys.version,
        'tests': {}
    }
    
    # Test pydantic import and functionality
    try:
        from pydantic import BaseModel, ValidationError
        
        class TestUser(BaseModel):
            name: str
            age: int
            email: str = None
        
        user = TestUser(name='Test User', age=30, email='test@example.com')
        
        try:
            invalid_user = TestUser(name='Test', age='invalid')
            results['tests']['pydantic'] = {'status': 'FAIL', 'error': 'Expected validation error'}
        except ValidationError:
            results['tests']['pydantic'] = {
                'status': 'PASS',
                'version': getattr(__import__('pydantic'), '__version__', 'unknown'),
                'test_data': user.model_dump()
            }
            
    except Exception as e:
        results['tests']['pydantic'] = {'status': 'FAIL', 'error': str(e)}
    
    # Test psycopg2 import and functionality  
    try:
        import psycopg2
        from psycopg2 import sql
        from psycopg2.extensions import parse_dsn
        
        query = sql.SQL("SELECT * FROM {} WHERE {} = %s").format(
            sql.Identifier('test_table'),
            sql.Identifier('id')
        )
        
        test_dsn = "host=localhost port=5432 dbname=testdb user=testuser password=testpass"
        parsed = parse_dsn(test_dsn)
        
        results['tests']['psycopg2'] = {
            'status': 'PASS',
            'version': psycopg2.__version__,
            'sql_composition': str(query),
            'dsn_parsed': len(parsed) > 0
        }
        
    except Exception as e:
        results['tests']['psycopg2'] = {'status': 'FAIL', 'error': str(e)}
    
    # Test integration
    try:
        from pydantic import BaseModel
        import psycopg2.extensions
        
        class DatabaseConfig(BaseModel):
            host: str
            port: int = 5432
            database: str
            user: str
            password: str
            
            def get_dsn(self):
                return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"
        
        config = DatabaseConfig(
            host='localhost',
            database='testdb', 
            user='testuser',
            password='testpass'
        )
        
        dsn = config.get_dsn()
        parsed = psycopg2.extensions.parse_dsn(dsn)
        
        results['tests']['integration'] = {
            'status': 'PASS',
            'config_validation': True,
            'dsn_generation': dsn,
            'dsn_validation': len(parsed) == 5
        }
        
    except Exception as e:
        results['tests']['integration'] = {'status': 'FAIL', 'error': str(e)}
    
    # Overall status
    all_passed = all(test.get('status') == 'PASS' for test in results['tests'].values())
    
    if not all_passed:
        results['statusCode'] = 500
    
    results['overall_status'] = 'PASS' if all_passed else 'FAIL'
    
    return {
        'statusCode': results['statusCode'],
        'body': json.dumps(results, indent=2)
    }