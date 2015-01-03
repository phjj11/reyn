﻿using System;
using System.Collections.Generic;
using System.IO;
using LeagueSharp.Network.Serialization;
using LeagueSharp.Network.Util;

namespace LeagueSharp.Network.Packets
{
    public class PKT_NPC_UpgradeSpellReq : Packet, ISerialized
    {
        private readonly SerializedData<Int32> _cheatModuleHash = new SerializedData<Int32>(10, 3, new List<uint>
        {
            0x27AD44AD,
            0,
            unchecked ((uint) -1),
            0,
            0x2C414950,
            0x2D7C723B,
            2,
            1
        });

        private readonly SerializedData<Int32> _cheatModuleInfo1 = new SerializedData<Int32>(7, 3, new List<uint>
        {
            1,
            0xE9558054,
            0x8D8AFC5F,
            2,
            0,
            unchecked((uint) -1),
            0,
            0xFD7AF57D
        });

        private readonly SerializedData<Int32> _cheatModuleInfo2 = new SerializedData<Int32>(4, 3, new List<uint>
        {
            0x7F946157,
            0x4C6EE815,
            1,
            0,
            2,
            unchecked ((uint) -1),
            0,
            0x212E9196
        });

        private readonly SerializedData<Byte> _spellSlot = new SerializedData<Byte>(0, 3, new List<uint>
        {
            0x6501D62E,
            2,
            1,
            0x87CFCD92,
            0xFE0A65A2,
            0,
            0xFF,
            0x21BD274B
        });

        public Int32 CheatModuleInfo1
        {
            get { return _cheatModuleInfo1.Data; }
            set { _cheatModuleInfo1.Data = value; }
        }

        public Byte SpellSlot
        {
            get { return _spellSlot.Data; }
            set { _spellSlot.Data = value; }
        }

        public Int32 CheatModuleHash
        {
            get { return _cheatModuleHash.Data; }
            set { _cheatModuleHash.Data = value; }
        }

        public Int32 CheatModuleInfo2
        {
            get { return _cheatModuleInfo2.Data; }
            set { _cheatModuleInfo2.Data = value; }
        }

        public Byte Evolve { get; set; }

        public bool Decode(byte[] data)
        {
            var reader = new BinaryReader(new MemoryStream(data));

            PacketId = reader.ReadInt16();
            NetworkId = reader.ReadInt32();

            var bitmask = reader.ReadUInt16();

            _cheatModuleInfo1.Decode(bitmask, reader);
            _spellSlot.Decode(bitmask, reader);
            _cheatModuleHash.Decode(bitmask, reader);
            _cheatModuleInfo2.Decode(bitmask, reader);
            Evolve = (byte) (bitmask.GetBits(3, 1) == 1 ? 1 : 0xFE);

            return true;
        }

        public byte[] Encode()
        {
            var ms = new MemoryStream();
            var writer = new BinaryWriter(ms);

            ushort bitmask = 0;

            _cheatModuleInfo1.Encode(ref bitmask, writer);
            _spellSlot.Encode(ref bitmask, writer);
            _cheatModuleHash.Encode(ref bitmask, writer);
            _cheatModuleInfo2.Encode(ref bitmask, writer);
            bitmask = bitmask.SetRange(3, 1, (ushort) (Evolve == 1 ? 1 : 0));

            var packet = new byte[ms.Length + 8];
            BitConverter.GetBytes(PacketId).CopyTo(packet, 0);
            BitConverter.GetBytes(NetworkId).CopyTo(packet, 2);
            BitConverter.GetBytes(bitmask).CopyTo(packet, 6);
            Array.Copy(ms.GetBuffer(), 0, packet, 8, ms.Length);

            return packet;
        }
    }
}