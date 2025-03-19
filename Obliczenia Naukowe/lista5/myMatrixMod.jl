#Paweł Kędzierski 272400
module myMatrixMod
using SparseArrays

mutable struct myMatrix
    size::Int64
    block_size::Int64
    matrix::SparseMatrixCSC{Float64, Int64}
end
end
