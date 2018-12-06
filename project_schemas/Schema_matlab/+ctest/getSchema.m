function obj = getSchema
persistent schemaObject
if isempty(schemaObject)
    schemaObject = dj.Schema(dj.conn, 'ctest', 'conrad_test');
end
obj = schemaObject;
end
