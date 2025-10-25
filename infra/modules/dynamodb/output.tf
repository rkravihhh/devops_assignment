output "table_arn" {
  description = "The arn of the table"
  value       = aws_dynamodb_table.main.arn
}

output "table_name" {
  description = "The name of the table"
  value       = aws_dynamodb_table.main.name
}

output "table_id" {
  description = "The ID of the table"
  value       = aws_dynamodb_table.main.id
}

output "table_stream_arn" {
  description = "The ARN of the Table Stream"
  value       = aws_dynamodb_table.main.stream_arn
}

output "table_stream_label" {
  description = "A timestamp, in ISO 8601 format, for this stream"
  value       = aws_dynamodb_table.main.stream_label
}
