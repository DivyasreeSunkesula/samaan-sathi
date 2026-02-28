import json
import os
import boto3
import base64
from typing import Dict, Any, List

textract = boto3.client('textract')
s3 = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process bill/receipt images using Textract and extract structured data
    """
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Get image from S3 or base64
        if 's3Key' in body:
            result = process_s3_image(body['s3Key'])
        elif 'imageBase64' in body:
            result = process_base64_image(body['imageBase64'])
        else:
            return response(400, {'error': 'Image source required (s3Key or imageBase64)'})
        
        # Extract structured data using Bedrock
        structured_data = extract_structured_data(result)
        
        return response(200, {
            'rawText': result.get('text'),
            'structuredData': structured_data,
            'confidence': result.get('confidence')
        })
        
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return response(500, {'error': str(e)})


def process_s3_image(s3_key: str) -> Dict[str, Any]:
    """Process image from S3 using Textract"""
    try:
        bucket = os.environ['DATA_BUCKET']
        
        # Use Textract AnalyzeExpense for bill processing
        response = textract.analyze_expense(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': s3_key
                }
            }
        )
        
        return parse_textract_response(response)
        
    except Exception as e:
        print(f"S3 OCR error: {str(e)}")
        raise


def process_base64_image(image_base64: str) -> Dict[str, Any]:
    """Process base64 encoded image using Textract"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_base64)
        
        # Use Textract AnalyzeExpense
        response = textract.analyze_expense(
            Document={'Bytes': image_bytes}
        )
        
        return parse_textract_response(response)
        
    except Exception as e:
        print(f"Base64 OCR error: {str(e)}")
        raise


def parse_textract_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Textract response and extract key information"""
    result = {
        'text': '',
        'items': [],
        'total': 0,
        'date': None,
        'vendor': None,
        'confidence': 0
    }
    
    try:
        expense_documents = response.get('ExpenseDocuments', [])
        
        if not expense_documents:
            return result
        
        doc = expense_documents[0]
        
        # Extract summary fields (vendor, date, total)
        for field in doc.get('SummaryFields', []):
            field_type = field.get('Type', {}).get('Text', '')
            value = field.get('ValueDetection', {}).get('Text', '')
            confidence = field.get('ValueDetection', {}).get('Confidence', 0)
            
            if 'VENDOR' in field_type.upper():
                result['vendor'] = value
            elif 'DATE' in field_type.upper():
                result['date'] = value
            elif 'TOTAL' in field_type.upper():
                try:
                    result['total'] = float(value.replace(',', '').replace('₹', '').strip())
                except:
                    pass
        
        # Extract line items
        for line_group in doc.get('LineItemGroups', []):
            for line_item in line_group.get('LineItems', []):
                item = {}
                for field in line_item.get('LineItemExpenseFields', []):
                    field_type = field.get('Type', {}).get('Text', '')
                    value = field.get('ValueDetection', {}).get('Text', '')
                    
                    if 'ITEM' in field_type.upper():
                        item['name'] = value
                    elif 'QUANTITY' in field_type.upper():
                        try:
                            item['quantity'] = float(value)
                        except:
                            item['quantity'] = 1
                    elif 'PRICE' in field_type.upper():
                        try:
                            item['price'] = float(value.replace(',', '').replace('₹', '').strip())
                        except:
                            pass
                
                if item.get('name'):
                    result['items'].append(item)
        
        # Calculate average confidence
        all_confidences = []
        for field in doc.get('SummaryFields', []):
            conf = field.get('ValueDetection', {}).get('Confidence', 0)
            if conf > 0:
                all_confidences.append(conf)
        
        if all_confidences:
            result['confidence'] = sum(all_confidences) / len(all_confidences)
        
        return result
        
    except Exception as e:
        print(f"Parse error: {str(e)}")
        return result


def extract_structured_data(ocr_result: Dict[str, Any]) -> Dict[str, Any]:
    """Use Bedrock to extract and structure data from OCR text"""
    try:
        prompt = f"""
        Extract structured sales data from this bill/receipt OCR result:
        
        Vendor: {ocr_result.get('vendor', 'Unknown')}
        Date: {ocr_result.get('date', 'Unknown')}
        Total: {ocr_result.get('total', 0)}
        Items: {json.dumps(ocr_result.get('items', []))}
        
        Return a JSON object with:
        - date (YYYY-MM-DD format)
        - items (array with name, quantity, price for each)
        - total
        - vendor
        
        Only return valid JSON, no explanation.
        """
        
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Extract JSON from response
        start = content.find('{')
        end = content.rfind('}') + 1
        if start >= 0 and end > start:
            structured = json.loads(content[start:end])
            return structured
        
        return ocr_result
        
    except Exception as e:
        print(f"Bedrock extraction error: {str(e)}")
        return ocr_result


def response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Format API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
